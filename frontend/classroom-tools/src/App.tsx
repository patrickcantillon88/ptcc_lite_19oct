import { useState, useEffect } from 'react'
import './App.css'

// Types
interface Student {
  id: number;
  name: string;
  class_code: string;
  year_group: string;
  support_level: number;
  avg_score?: number;
  behavior_score?: number;
}

interface ClassData {
  classes: string[];
}

interface GroupData {
  class_code: string;
  total_students: number;
  num_groups: number;
  rationale: string;
  groups: Group[];
}

interface Group {
  group_number: number;
  members: Student[];
  group_stats: {
    size: number;
    avg_assessment_score: number;
    total_support_level: number;
    avg_behavior_score: number;
  };
}

interface DifferentiationData {
  class_code: string;
  subject: string;
  total_students: number;
  summary: {
    extension_count: number;
    on_level_count: number;
    support_count: number;
    avg_class_score?: number;
  };
  suggested_groups: {
    level: 'extension' | 'on_level' | 'support' | 'high_support';
    group_name: string;
    student_count: number;
    students: string[];
    focus: string;
    strategies: string[];
  }[];
}

function App() {
  const [activeTab, setActiveTab] = useState<'intervention' | 'progress' | 'seating' | 'groups' | 'differentiation'>('groups');
  const [classes, setClasses] = useState<string[]>([]);
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [groupData, setGroupData] = useState<GroupData | null>(null);
  const [differentiationData, setDifferentiationData] = useState<DifferentiationData | null>(null);
  const [groupSize, setGroupSize] = useState(4);
  const [groupStrategy, setGroupStrategy] = useState<'mixed_ability' | 'similar_ability' | 'behavioral_balance' | 'support_aware'>('mixed_ability');
  const [subject, setSubject] = useState('');
  
  // Load available classes on mount
  useEffect(() => {
    fetchClasses();
  }, []);
  
  const fetchClasses = async () => {
    try {
      const response = await fetch('/api/classroom-tools/classes');
      if (response.ok) {
        const data: ClassData = await response.json();
        setClasses(data.classes || []);
        if (data.classes && data.classes.length > 0) {
          setSelectedClass(data.classes[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch classes:', error);
    }
  };
  
  const generateGroups = async () => {
    if (!selectedClass) return;
    
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        class_code: selectedClass,
        group_size: groupSize.toString(),
        strategy: groupStrategy
      });
      
      const response = await fetch(`/api/classroom-tools/group-formation?${params}`);
      if (response.ok) {
        const data: GroupData = await response.json();
        setGroupData(data);
      }
    } catch (error) {
      console.error('Failed to generate groups:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const analyzeDifferentiation = async () => {
    if (!selectedClass) return;
    
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        class_code: selectedClass,
        ...(subject && { subject })
      });
      
      const response = await fetch(`/api/classroom-tools/differentiation-support?${params}`);
      if (response.ok) {
        const data: DifferentiationData = await response.json();
        setDifferentiationData(data);
      }
    } catch (error) {
      console.error('Failed to analyze differentiation:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const strategyDescriptions = {
    mixed_ability: '🎯 Mix high and low performers to promote peer learning',
    similar_ability: '📚 Group similar performers for targeted instruction',
    behavioral_balance: '⚖️ Distribute behavioral dynamics evenly across groups',
    support_aware: '🫂 Distribute support needs evenly for teacher management'
  };
  
  const levelColors = {
    extension: '🟢',
    on_level: '🟡',
    support: '🟠',
    high_support: '🔴'
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Classroom Management Tools</h1>
          <p className="text-gray-600">Data-driven tools to support classroom management and student interventions</p>
        </header>
        
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-6">
          <nav className="flex px-6 tab-nav" aria-label="Tabs">
            {[
              { key: 'intervention', label: '🚨 Intervention Priority', disabled: true },
              { key: 'progress', label: '📈 Progress Dashboard', disabled: true },
              { key: 'seating', label: '🪑 Seating Chart', disabled: true },
              { key: 'groups', label: '👥 Group Formation' },
              { key: 'differentiation', label: '🎯 Differentiation' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => !tab.disabled && setActiveTab(tab.key as any)}
                disabled={tab.disabled}
                className={activeTab === tab.key ? 'active' : ''}
              >
                {tab.label}
                {tab.disabled && <span style={{marginLeft: '0.5rem', fontSize: '0.75rem'}}>(Coming Soon)</span>}
              </button>
            ))}
          </nav>
        </div>
        
        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'groups' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">👥 Student Group Formation</h2>
              <p className="text-gray-600 mb-6">Generate optimal student groups based on assessment data, behavior patterns, and support needs</p>
              
              {/* Controls */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Select Class</label>
                  <select
                    value={selectedClass}
                    onChange={(e) => setSelectedClass(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    {classes.map(cls => (
                      <option key={cls} value={cls}>{cls}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Group Size</label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={groupSize}
                    onChange={(e) => setGroupSize(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Grouping Strategy</label>
                  <select
                    value={groupStrategy}
                    onChange={(e) => setGroupStrategy(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="mixed_ability">Mixed Ability</option>
                    <option value="similar_ability">Similar Ability</option>
                    <option value="behavioral_balance">Behavioral Balance</option>
                    <option value="support_aware">Support Aware</option>
                  </select>
                </div>
              </div>
              
              {/* Strategy Description */}
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p className="text-blue-800">{strategyDescriptions[groupStrategy]}</p>
              </div>
              
              {/* Generate Button */}
              <button
                onClick={generateGroups}
                disabled={isLoading || !selectedClass}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed mb-6"
              >
                {isLoading ? '⏳ Generating Groups...' : '✨ Generate Groups'}
              </button>
              
              {/* Results */}
              {groupData && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold mb-4">
                    🎯 Generated Groups for {groupData.class_code}
                  </h3>
                  <p className="text-gray-600 mb-2">
                    <strong>Strategy:</strong> {strategyDescriptions[groupStrategy]}
                  </p>
                  <p className="text-gray-600 mb-4">
                    <strong>Total Students:</strong> {groupData.total_students} | <strong>Groups Created:</strong> {groupData.num_groups}
                  </p>
                  {groupData.rationale && (
                    <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
                      <p className="text-green-800">✅ {groupData.rationale}</p>
                    </div>
                  )}
                  
                  <div className="space-y-4">
                    {groupData.groups.map((group) => (
                      <div key={group.group_number} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <h4 className="font-semibold text-lg">
                            👥 Group {group.group_number} - {group.group_stats.size} students
                          </h4>
                          <span className="text-sm text-gray-500">
                            Avg Score: {group.group_stats.avg_assessment_score}%
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div className="text-center">
                            <div className="text-sm text-gray-500">Avg Assessment Score</div>
                            <div className="font-semibold">{group.group_stats.avg_assessment_score}%</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-500">Total Support Level</div>
                            <div className="font-semibold">{group.group_stats.total_support_level}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-500">Avg Behavior Score</div>
                            <div className="font-semibold">
                              {group.group_stats.avg_behavior_score >= 0 ? '+' : ''}{group.group_stats.avg_behavior_score.toFixed(1)}
                            </div>
                          </div>
                        </div>
                        
                        <div>
                          <h5 className="font-medium mb-2">Members:</h5>
                          <div className="space-y-1">
                            {group.members.map((member) => {
                              const supportIcon = ['🟢', '🟡', '🟠', '🔴'][member.support_level] || '⚪';
                              const behaviorIcon = (member.behavior_score || 0) >= 0 ? '🟢' : '🔴';
                              return (
                                <div key={member.id} className="text-sm">
                                  {supportIcon} <strong>{member.name}</strong> - 
                                  Avg: {member.avg_score || 0}% | 
                                  Behavior: {behaviorIcon} {(member.behavior_score || 0) >= 0 ? '+' : ''}{member.behavior_score || 0} | 
                                  Support: Level {member.support_level}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'differentiation' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">🎯 Differentiation Decision Support</h2>
              <p className="text-gray-600 mb-6">Identify students' learning levels and plan differentiated instruction based on assessment data</p>
              
              {/* Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Select Class</label>
                  <select
                    value={selectedClass}
                    onChange={(e) => setSelectedClass(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    {classes.map(cls => (
                      <option key={cls} value={cls}>{cls}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Subject (optional)</label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., Math, English"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              {/* Analyze Button */}
              <button
                onClick={analyzeDifferentiation}
                disabled={isLoading || !selectedClass}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed mb-6"
              >
                {isLoading ? '⏳ Analyzing...' : '✨ Analyze Class for Differentiation'}
              </button>
              
              {/* Results */}
              {differentiationData && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold mb-4">
                    📊 Analysis Results for {differentiationData.class_code}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    <strong>Subject:</strong> {differentiationData.subject}
                  </p>
                  
                  {/* Summary Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-sm text-gray-500">Total Students</div>
                      <div className="font-semibold text-lg">{differentiationData.total_students}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-500">Extension</div>
                      <div className="font-semibold text-lg text-green-600">{differentiationData.summary.extension_count}</div>
                      <div className="text-xs text-gray-500">Ready for challenge</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-500">On-Level</div>
                      <div className="font-semibold text-lg text-yellow-600">{differentiationData.summary.on_level_count}</div>
                      <div className="text-xs text-gray-500">Meeting grade level</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-500">Need Support</div>
                      <div className="font-semibold text-lg text-orange-600">{differentiationData.summary.support_count}</div>
                      <div className="text-xs text-gray-500">Below grade level</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-500">Class Avg</div>
                      <div className="font-semibold text-lg">
                        {differentiationData.summary.avg_class_score ? `${differentiationData.summary.avg_class_score}%` : 'N/A'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Suggested Groups */}
                  <h4 className="text-lg font-semibold mb-4">🎯 Suggested Instructional Groups</h4>
                  {differentiationData.suggested_groups.length > 0 ? (
                    <div className="space-y-4">
                      {differentiationData.suggested_groups.map((group, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <h5 className="font-semibold mb-2">
                            {levelColors[group.level]} {group.group_name} ({group.student_count} students)
                          </h5>
                          <p className="text-gray-700 mb-3">
                            <strong>Focus:</strong> {group.focus}
                          </p>
                          
                          <div className="mb-3">
                            <h6 className="font-medium mb-2">Students:</h6>
                            <div className="grid grid-cols-3 gap-2">
                              {group.students.map((student, studentIndex) => (
                                <div key={studentIndex} className="text-sm">• {student}</div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h6 className="font-medium mb-2">Recommended Strategies:</h6>
                            <ul className="space-y-1">
                              {group.strategies.map((strategy, strategyIndex) => (
                                <li key={strategyIndex} className="text-sm">✅ {strategy}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                      <p className="text-blue-800">No groupings could be generated (insufficient assessment data)</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* Placeholder for other tabs */}
          {['intervention', 'progress', 'seating'].includes(activeTab) && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🚧</div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">Coming Soon</h3>
              <p className="text-gray-500">This feature is under development and will be available in a future update.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
