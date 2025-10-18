"""
AccommodationComplianceAgent: Generates pre-lesson accommodation checklists.

Ensures all student accommodations are active and properly implemented
10 minutes before each lesson by creating actionable checklists organized by:
- Sensory accommodations (lighting, noise, seating)
- Behavioral accommodations (movement breaks, de-escalation setup)
- Social accommodations (peer buddy, inclusion strategy)
- Communication accommodations (speech/language support)
"""

from datetime import datetime
from typing import List, Dict, Any
from backend.core.base_agent import BaseAgent, StudentContext, AgentOutput


class AccommodationComplianceAgent(BaseAgent):
    """
    Pre-lesson accommodation compliance agent.
    
    Generates actionable checklists ensuring all accommodations are in place.
    Organizes by category and provides implementation details.
    """
    
    def __init__(self):
        super().__init__("AccommodationComplianceAgent")
    
    def analyze(self, context: StudentContext) -> AgentOutput:
        """Generate accommodation compliance checklist."""
        
        if not context.active_accommodations:
            return AgentOutput(
                agent_name=self.name,
                timestamp=datetime.now(),
                student_id=context.student_id,
                title=f"✅ NO ACCOMMODATIONS - {context.current_time.strftime('%H:%M')} {context.current_subject}",
                message=f"No active accommodations for {context.student_name}. Standard lesson approach.",
                priority='low',
                intervention_type='preventive',
                action_required=False,
                recommended_actions=["Standard lesson setup"],
                reasoning="No accommodations documented"
            )
        
        # Organize accommodations by type
        organized = self._organize_by_type(context.active_accommodations)
        
        # Generate checklists
        checklists = self._generate_checklists(context, organized)
        
        # Determine priority based on accommodation count and types
        priority = self._determine_priority(organized)
        
        # Format message
        message = self._format_checklist(
            context=context,
            checklists=checklists,
            total_accommodations=len(context.active_accommodations)
        )
        
        # Generate recommendations
        recommendations = self._generate_setup_recommendations(context, organized)
        
        return AgentOutput(
            agent_name=self.name,
            timestamp=datetime.now(),
            student_id=context.student_id,
            title=f"✅ LESSON SETUP CHECKLIST - {context.current_time.strftime('%H:%M')} {context.current_subject} ({context.class_code})",
            message=message,
            priority=priority,
            intervention_type='preventive',
            action_required=len(context.active_accommodations) > 0,
            recommended_actions=recommendations,
            reasoning=f"{len(context.active_accommodations)} accommodations require setup verification"
        )
    
    def _organize_by_type(self, accommodations: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
        """Organize accommodations by type."""
        organized = {
            'sensory': [],
            'behavioral': [],
            'social': [],
            'communication': [],
            'equipment': [],
            'schedule': [],
            'other': []
        }
        
        for acc in accommodations:
            acc_type = acc.get('accommodation_type', 'other').lower()
            if acc_type in organized:
                organized[acc_type].append(acc)
            else:
                organized['other'].append(acc)
        
        return organized
    
    def _generate_checklists(
        self,
        context: StudentContext,
        organized: Dict[str, List[Dict]]
    ) -> Dict[str, List[str]]:
        """Generate checklist items for each accommodation type."""
        checklists = {}
        
        # Sensory accommodations
        if organized['sensory']:
            checklists['sensory'] = self._generate_sensory_checklist(
                context,
                organized['sensory']
            )
        
        # Behavioral accommodations
        if organized['behavioral']:
            checklists['behavioral'] = self._generate_behavioral_checklist(
                context,
                organized['behavioral']
            )
        
        # Social accommodations
        if organized['social']:
            checklists['social'] = self._generate_social_checklist(
                context,
                organized['social']
            )
        
        # Communication accommodations
        if organized['communication']:
            checklists['communication'] = self._generate_communication_checklist(
                context,
                organized['communication']
            )
        
        # Equipment accommodations
        if organized['equipment']:
            checklists['equipment'] = self._generate_equipment_checklist(
                context,
                organized['equipment']
            )
        
        # Schedule accommodations
        if organized['schedule']:
            checklists['schedule'] = self._generate_schedule_checklist(
                context,
                organized['schedule']
            )
        
        return checklists
    
    def _generate_sensory_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate sensory environment checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'light' in desc:
                items.append(f"☐ Lighting: Adjust for {context.student_name} (light sensitivity)")
            
            if 'noise' in desc or 'sound' in desc or 'audio' in desc:
                items.append(f"☐ Noise: Have ear defenders available for {context.student_name}")
            
            if 'sensory' in desc or 'overload' in desc:
                items.append(f"☐ Sensory: Minimize overstimulation for {context.student_name}")
            
            if 'seat' in desc or 'position' in desc:
                items.append(f"☐ Seating: Position {context.student_name} appropriately")
        
        return items if items else [f"☐ Review sensory environment for {context.student_name}"]
    
    def _generate_behavioral_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate behavioral support checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'movement' in desc or 'break' in desc:
                items.append(f"☐ Movement: Schedule movement breaks for {context.student_name} during lesson")
            
            if 'impuls' in desc or 'boundary' in desc:
                items.append(f"☐ Boundaries: Establish clear expectations with {context.student_name} at start")
            
            if 'anxiety' in desc or 'reassur' in desc:
                items.append(f"☐ Reassurance: Assign buddy or TA for check-ins with {context.student_name}")
            
            if 'de-escalat' in desc or 'cool' in desc:
                items.append(f"☐ De-escalation: Have cool-down space ready for {context.student_name}")
            
            if 'attention' in desc:
                items.append(f"☐ Attention: Use proximity and cues for {context.student_name}")
        
        return items if items else [f"☐ Establish behavioral supports for {context.student_name}"]
    
    def _generate_social_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate social/peer support checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'peer' in desc or 'buddy' in desc:
                items.append(f"☐ Peer Buddy: Assign compatible peer to support {context.student_name}")
            
            if 'isolation' in desc or 'withdraw' in desc:
                items.append(f"☐ Inclusion: Actively involve {context.student_name} in group activities")
            
            if 'conflict' in desc:
                items.append(f"☐ Conflict: Monitor peer interactions with {context.student_name}")
            
            if 'social' in desc:
                items.append(f"☐ Social Skills: Facilitate structured peer interaction for {context.student_name}")
        
        return items if items else [f"☐ Monitor social interactions for {context.student_name}"]
    
    def _generate_communication_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate communication support checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'speech' in desc or 'language' in desc or 'slt' in desc:
                items.append(f"☐ Speech/Language: Position 1:1 support for {context.student_name} if available")
            
            if 'verbal' in desc or 'communication' in desc:
                items.append(f"☐ Communication: Use visual supports and alternatives for {context.student_name}")
            
            if 'mutism' in desc or 'selective' in desc:
                items.append(f"☐ Selective Mutism: Use low-pressure techniques with {context.student_name}")
        
        return items if items else [f"☐ Support communication for {context.student_name}"]
    
    def _generate_equipment_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate equipment/device checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'filter' in desc or 'screen' in desc or 'device' in desc:
                items.append(f"☐ Devices: Ensure blue-light filters/devices ready for {context.student_name}")
            
            if 'computer' in desc or 'ipad' in desc or 'tablet' in desc:
                items.append(f"☐ Tech: Check accessibility settings on devices for {context.student_name}")
        
        return items if items else [f"☐ Verify equipment for {context.student_name}"]
    
    def _generate_schedule_checklist(
        self,
        context: StudentContext,
        accommodations: List[Dict]
    ) -> List[str]:
        """Generate schedule/timing checklist."""
        items = []
        
        for acc in accommodations:
            desc = acc.get('description', '').lower()
            
            if 'transition' in desc or 'warning' in desc:
                items.append(f"☐ Transitions: Provide warnings and visual schedules for {context.student_name}")
            
            if 'timing' in desc or 'pacing' in desc:
                items.append(f"☐ Pacing: Allow extra time for {context.student_name} where needed")
        
        return items if items else [f"☐ Review schedule adjustments for {context.student_name}"]
    
    def _determine_priority(self, organized: Dict[str, List[Dict]]) -> str:
        """Determine priority based on accommodation complexity."""
        total = sum(len(items) for items in organized.values())
        
        if total >= 5:
            return 'high'
        elif total >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _format_checklist(
        self,
        context: StudentContext,
        checklists: Dict[str, List[str]],
        total_accommodations: int
    ) -> str:
        """Format checklists into message."""
        lines = [f"\n✅ LESSON SETUP CHECKLIST - {context.current_time.strftime('%H:%M')} {context.current_subject}"]
        lines.append(f"Student: {context.student_name} | Class: {context.class_code}\n")
        
        section_headers = {
            'sensory': '👁️ SENSORY/ENVIRONMENT',
            'behavioral': '💭 BEHAVIOR SUPPORT',
            'social': '👥 SOCIAL/PEER SUPPORT',
            'communication': '🗣️ COMMUNICATION',
            'equipment': '🖥️ EQUIPMENT',
            'schedule': '⏰ SCHEDULE/TIMING'
        }
        
        for section_key, header in section_headers.items():
            if section_key in checklists:
                lines.append(f"{header}:")
                for item in checklists[section_key]:
                    lines.append(f"  {item}")
                lines.append("")
        
        # Add summary
        lines.append(f"📋 SETUP SUMMARY: {total_accommodations} accommodations to implement")
        lines.append(f"⏱️ Estimated setup time: {2 if total_accommodations <= 3 else 3 if total_accommodations <= 5 else 5} minutes")
        
        return "\n".join(lines)
    
    def _generate_setup_recommendations(
        self,
        context: StudentContext,
        organized: Dict[str, List[Dict]]
    ) -> List[str]:
        """Generate specific setup recommendations."""
        recommendations = []
        
        total = sum(len(items) for items in organized.values())
        
        if total >= 5:
            recommendations.append("Allow extra time for comprehensive setup")
        
        if organized['sensory']:
            recommendations.append("Adjust classroom environment before lesson")
        
        if organized['behavioral']:
            recommendations.append(f"Brief {context.student_name} on expectations at lesson start")
        
        if organized['social']:
            recommendations.append(f"Assign peer buddy before class begins")
        
        if organized['communication']:
            recommendations.append(f"Position communication support for {context.student_name}")
        
        if organized['equipment']:
            recommendations.append(f"Test all devices/filters before lesson")
        
        if organized['schedule']:
            recommendations.append(f"Display visual schedule for {context.student_name}")
        
        return recommendations if recommendations else ["Standard lesson setup"]
