import { useState, useEffect, useCallback } from 'react';

interface NotificationSettings {
  enabled: boolean;
  reminders: boolean;
  logs: boolean;
  system: boolean;
}

interface UseNotificationsReturn {
  isSupported: boolean;
  permission: NotificationPermission;
  settings: NotificationSettings;
  requestPermission: () => Promise<NotificationPermission>;
  sendNotification: (title: string, options?: NotificationOptions) => void;
  scheduleReminder: (title: string, delay: number) => number;
  clearReminder: (id: number) => void;
  updateSettings: (newSettings: Partial<NotificationSettings>) => void;
}

const defaultSettings: NotificationSettings = {
  enabled: false,
  reminders: true,
  logs: false,
  system: true,
};

export const useNotifications = (): UseNotificationsReturn => {
  const [isSupported] = useState(() => 'Notification' in window);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [settings, setSettings] = useState<NotificationSettings>(defaultSettings);
  const [scheduledNotifications, setScheduledNotifications] = useState<Map<number, number>>(new Map());

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('ptccNotificationSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsed });
      } catch (error) {
        console.error('Failed to parse notification settings:', error);
      }
    }

    // Check current permission status
    if (isSupported) {
      setPermission(Notification.permission);
    }
  }, [isSupported]);

  // Update settings in localStorage whenever they change
  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>) => {
    const updatedSettings = { ...settings, ...newSettings };
    setSettings(updatedSettings);
    localStorage.setItem('ptccNotificationSettings', JSON.stringify(updatedSettings));
  }, [settings]);

  // Request notification permission
  const requestPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (!isSupported) {
      throw new Error('Notifications not supported');
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);

      if (result === 'granted') {
        updateSettings({ enabled: true });
      }

      return result;
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      throw error;
    }
  }, [isSupported, updateSettings]);

  // Send notification if permitted and enabled
  const sendNotification = useCallback((title: string, options: NotificationOptions = {}) => {
    if (!isSupported || permission !== 'granted' || !settings.enabled) {
      return;
    }

    try {
      const notification = new Notification(title, {
        icon: '/pwa-192x192.png',
        badge: '/pwa-192x192.png',
        ...options,
      });

      // Auto-close after 5 seconds
      setTimeout(() => {
        notification.close();
      }, 5000);

      return notification;
    } catch (error) {
      console.error('Failed to send notification:', error);
    }
  }, [isSupported, permission, settings.enabled]);

  // Schedule a reminder notification
  const scheduleReminder = useCallback((title: string, delay: number): number => {
    if (!settings.enabled || !settings.reminders) {
      return 0;
    }

    const id = Date.now() + Math.random();
    const timeoutId = window.setTimeout(() => {
      sendNotification(title, {
        body: 'Reminder from PTCC Mobile',
        tag: 'reminder',
        requireInteraction: false,
      });
      setScheduledNotifications(prev => {
        const newMap = new Map(prev);
        newMap.delete(id);
        return newMap;
      });
    }, delay);

    setScheduledNotifications(prev => new Map(prev.set(id, timeoutId)));
    return id;
  }, [settings.enabled, settings.reminders, sendNotification]);

  // Clear a scheduled reminder
  const clearReminder = useCallback((id: number) => {
    const timeoutId = scheduledNotifications.get(id);
    if (timeoutId) {
      clearTimeout(timeoutId);
      setScheduledNotifications(prev => {
        const newMap = new Map(prev);
        newMap.delete(id);
        return newMap;
      });
    }
  }, [scheduledNotifications]);

  // Cleanup scheduled notifications on unmount
  useEffect(() => {
    return () => {
      scheduledNotifications.forEach(timeoutId => clearTimeout(timeoutId));
    };
  }, [scheduledNotifications]);

  return {
    isSupported,
    permission,
    settings,
    requestPermission,
    sendNotification,
    scheduleReminder,
    clearReminder,
    updateSettings,
  };
};

export default useNotifications;