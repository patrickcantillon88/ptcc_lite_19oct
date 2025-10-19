# LUNAR BASE RECONSTRUCTION
## Lesson 1: Reconstructing Your Base
**Year 5 - Age 10**

### Slide 1: Lesson Title
**LUNAR BASE RECONSTRUCTION**  
Lesson 1: Reconstructing Your Base  
Year 5 - Age 10

### Slide 2: Lesson Objectives
By the end of this lesson, you will be able to:
- Analyze a completed lunar base to understand how parts connect
- Build your own unique base layout using the starter components
- Position domes, tubes, and airlocks in logical places
- Add characters from the library to bring your base to life
- Make a character move around your base using code blocks

**Key Skills:** Spatial thinking, building with modules, basic animation

### Slide 3: Input - Teacher Shows Example
Look at this completed lunar base: [Teacher shows example base on screen]

**Notice:**
- Different colored domes connected by tubes
- Airlock doors at entrance points
- Characters placed throughout the base
- Logical flow between different areas

**Your Starter Kit Contains:**
- Domes (can be copied and recolored)
- Tube segments for corridors
- Airlock doors
- Button groups
- Pre-positioned camera

**You Need to Add:** Characters from the library!

### Slide 4: Core Task - All Students Start Building
**Follow These Steps:**
1. Study the example base - how are parts connected?
2. Start with one dome as your main living area
3. Add tube segments to create corridors
4. Connect more domes with logical pathways
5. Position airlock doors at entrance points
6. Place button groups near doors
7. Add characters from the library

**Use this code to make a character patrol:**
```
when program starts
   move Regular_man on path Round_path in 120 sec forever
   set gravity pull to 0.17
```

**Remember:** Your base doesn't have to match the example - make it your own!

### Slide 5: Mini Plenary
**Check Your Progress - Ask Yourself:**
- ✓ Does your base have clear connections between areas?
- ✓ Is your character moving continuously around part of the base?
- ✓ Are your airlocks positioned at logical entry/exit points?
- ✓ Can you identify the purpose of each dome in your design?
- ✓ Did you successfully add characters from the library?

If you answered YES to most questions, you're ready for the next challenge!

### Slide 6: Foundation Challenge (LA)
#### BASIC 1-DOME BASE
**Your Mission:** Build a simple but functional lunar base for astronauts

**What You Need:**
- 1 dome as main habitat
- 1 airlock door at the entrance
- 1 character moving on the path

**Success Looks Like:**
- A secure main living area
- Clear entrance to the base
- One character patrolling around

**Perfect for:** Getting the basics right first!

### Slide 7: Intermediate Challenge (MA)
#### CONNECTED 2-DOME COMPLEX
**Your Mission:** Create a multi-area base with different purposes

**What You Need:**
- 2 domes with different functions (living, working)
- Tube segments connecting them
- 2 airlock doors for different entrances
- 2-3 characters placed around the base

**Success Looks Like:**
- Connected areas with logical flow
- Multiple entry points
- Characters in different locations

**Perfect for:** Building more complex structures!

### Slide 8: Advanced Challenge (HA)
#### MULTI-AREA 3-DOME NETWORK
**Your Mission:** Design a sophisticated lunar settlement

**What You Need:**
- 3+ specialized areas with unique colors
- Complex tube network connecting everything
- Strategic airlock placement
- Multiple characters with different roles
- Custom or modified patrol paths

**Success Looks Like:**
- Professional-quality design
- Innovative layout solutions
- Complex character interactions

**Perfect for:** Pushing your design skills to the limit!

### Slide 9: Plenary
**WHAT WE'VE ACHIEVED TODAY:**
- 🏗️ Built functional lunar bases from scratch
- 🧠 Used spatial reasoning and logical design thinking
- 🚀 Created realistic space habitats
- 👥 Brought bases to life with moving characters

**KEY LEARNING:** You've proven that complex structures can be built from simple components - just like real space missions! Your bases show real engineering thinking!

### Slide 10: Next Steps
**YOU'RE READY FOR LESSON 2!**

**What's Coming Next:**
- 🔘 Make your buttons actually open and close doors
- ⚖️ Add different gravity zones to your base areas
- 🏃 Program realistic character movement with physics
- 🎮 Create interactive systems that respond to clicks

**Your Challenge:** Keep your base safe - we'll be adding interactive systems next lesson!

**Well Done, Space Engineers!**

---

# LUNAR BASE RECONSTRUCTION
## Lesson 2: Interactive Systems Programming
**Year 5 - Age 10**

### Slide 1: Lesson Title
**LUNAR BASE RECONSTRUCTION**  
Lesson 2: Interactive Systems Programming  
Year 5 - Age 10

### Slide 2: Lesson Objectives
By the end of this lesson, you will be able to:
- Program buttons to control doors using "when clicked" events
- Apply different gravity settings to simulate space zones
- Use "push with velocity" to create realistic character movement
- Make objects behave differently in low-gravity environments
- Create systems that respond to user interactions

**Key Skills:** Event programming, physics simulation, cause and effect

### Slide 3: Input - Teacher Shows Example
Watch this interactive base in action: [Teacher demonstrates clicking buttons to open doors]

**See How:**
- Buttons make doors open and close automatically
- Characters jump differently in low gravity
- Different areas have different gravity effects
- Systems respond immediately to clicks

**Building on Your Base:** Your reconstructed base from Lesson 1 is perfect for adding interactivity! We'll make those buttons and doors actually work like real space systems.

### Slide 4: Core Task - All Students Start Programming
**Essential Code Blocks to Use:**

**Door Control System:**
```
when ButtonGroup1 is clicked
  move Air_Lock_Door1 to y: -2 in 2 sec
  wait 5 sec
  move Air_Lock_Door1 to y: 0 in 2 sec
```

**Character Physics:**
```
when Regular_man is clicked
  push Regular_man with velocity 2 forward

when program starts
  set gravity pull to 0.17
```

**Start Programming:** Make your buttons control your doors and add physics to your characters!

### Slide 5: Mini Plenary
**Test Your Interactive Systems:**
- ✓ Do your doors open and close when buttons are clicked?
- ✓ Can you make characters jump or move when clicked?
- ✓ Does the low gravity setting make objects behave differently?
- ✓ Are your interactive systems responding consistently?
- ✓ Do your doors close automatically after opening?

If your systems are working, you're ready for the challenge levels!

### Slide 6: Foundation Challenge (LA)
#### BASIC BUTTON-DOOR SYSTEM
**Your Mission:** Make your 1-dome base interactive with working systems

**What You Need to Program:**
- 1 button controls 1 door (open/close cycle)
- Characters respond to clicks with simple movement
- Set lunar gravity (0.17) for the entire base

**Success Looks Like:**
- Door opens when button is clicked, then closes automatically
- Characters move when you click them
- Everything feels lighter due to low gravity

**Perfect for:** Learning the basics of interactive programming!

### Slide 7: Intermediate Challenge (MA)
#### MULTIPLE INTERACTIVE SYSTEMS
**Your Mission:** Create independent control systems for your 2-dome complex

**What You Need to Program:**
- 2+ button-door pairs working separately
- Characters with different click responses (jumping, pushing)
- Different gravity in different areas
- Doors that give feedback (sounds or visual changes)

**Success Looks Like:**
- Multiple working systems that don't interfere with each other
- Varied character interactions throughout the base
- Different zones feel different to move through

**Perfect for:** Managing multiple systems at once!

### Slide 8: Advanced Challenge (HA)
#### COMPLEX BASE OPERATIONS
**Your Mission:** Create sophisticated control systems for your 3-dome network

**What You Need to Program:**
- Multiple gravity zones (different gravity in each dome)
- Emergency systems (all doors open at once)
- Advanced character behaviors affected by interactions
- Physics-based puzzles using gravity to move objects
- Complex timing sequences

**Success Looks Like:**
- Professional-level interaction design
- Creative problem-solving with physics
- Systems that work together seamlessly

**Perfect for:** Pushing programming skills to the limit!

### Slide 9: Plenary
**WHAT WE'VE ACHIEVED TODAY:**
- 🤖 Programmed interactive systems that respond to user input
- ⚖️ Simulated realistic space physics and gravity
- 🚪 Created working airlock systems like real space stations
- 🎮 Built responsive user interfaces

**KEY LEARNING:** Your bases now work like real space systems! You've learned how cause-and-effect programming makes technology respond to human actions. You're thinking like real space engineers!

### Slide 10: Next Steps
**YOU'RE READY FOR LESSON 3!**

**What's Coming Next:**
- 📋 Add information panels that teach about space science
- ❓ Create quiz systems to test space knowledge
- 📹 Design educational tours using camera movement
- 🎓 Transform your base into a teaching tool for others

**Your Challenge:** Your interactive base will become an educational experience that teaches others about space exploration!

**Excellent Programming, Space Engineers!**

---

# LUNAR BASE RECONSTRUCTION
## Lesson 3: Educational Information Systems
**Year 5 - Age 10**

### Slide 1: Lesson Title
**LUNAR BASE RECONSTRUCTION**  
Lesson 3: Educational Information Systems  
Year 5 - Age 10

### Slide 2: Lesson Objectives
By the end of this lesson, you will be able to:
- Create information panels that explain how your base works
- Design quiz systems that test space exploration knowledge
- Build educational tours using camera movement and timing
- Add text displays that teach real space science
- Transform your interactive base into a teaching tool for others

**Key Skills:** Information design, educational content, user experience, knowledge sharing

### Slide 3: Input - Teacher Shows Example
Watch this educational base in action: [Teacher demonstrates clicking domes to show info panels]

**See How:**
- Clicking domes shows information about their purpose
- Quiz questions test space knowledge with helpful feedback
- Camera moves to show different areas during tours
- Real space science facts are included

**Building on Your Interactive Base:** Your working doors and character systems from Lesson 2 provide perfect opportunities for educational content!

### Slide 4: Core Task - All Students Start Programming
**Essential Code Blocks to Use:**

**Information Panel System:**
```
when Dome_1 is clicked
  show info panel with title "Habitat Dome" 
  text "Living quarters with life support systems. Gravity set to 0.17g"
```

**Quiz System:**
```
when Space_Hanger is clicked
  show quiz panel with question "Why do lunar bases need airlocks?"
  correct answer "To prevent air loss"
  when correct: say "Correct! Air would escape into the vacuum of space"
  when incorrect: say "Think about what happens to air in space..."
```

**Start Programming:** Add educational content to teach others about your base!

### Slide 5: Mini Plenary
**Test Your Educational Systems:**
- ✓ Do your information panels provide useful facts about space exploration?
- ✓ Are your quiz questions appropriate for teaching others?
- ✓ Can users easily navigate and learn from your base?
- ✓ Does your educational content connect to real space science?
- ✓ Are your explanations clear and accurate?

If people can learn from your base, you're ready for the challenge levels!

### Slide 6: Foundation Challenge (LA)
#### BASIC INFORMATION SYSTEM
**Your Mission:** Make your 1-dome base teach others about space living

**What You Need to Create:**
- 2-3 information panels explaining your dome and airlock
- 1 simple quiz question about lunar gravity or space
- Clear, accurate information that your classmates can understand

**Success Looks Like:**
- Working info panels that appear when clicked
- Educational content that teaches real space facts
- Quiz with helpful feedback for wrong answers

**Perfect for:** Creating your first educational content!

### Slide 7: Intermediate Challenge (MA)
#### COMPREHENSIVE LEARNING EXPERIENCE
**Your Mission:** Create a rich educational experience for your 2-dome complex

**What You Need to Create:**
- 4+ detailed information panels covering different space topics
- 2-3 quiz questions with helpful feedback
- Guided introduction sequence for new users
- Mix of base-specific and general space science information

**Success Looks Like:**
- Rich educational content throughout the base
- Good user guidance for visitors
- Combination of facts about your base and real space science

**Perfect for:** Building comprehensive learning experiences!

### Slide 8: Advanced Challenge (HA)
#### INTERACTIVE SPACE EDUCATION CENTER
**Your Mission:** Transform your 3-dome network into a professional educational experience

**What You Need to Create:**
- 6+ information systems covering complex space science topics
- Multi-question quiz system with scoring
- Multiple tour modes (construction, daily life, science, emergency)
- Interactive experiments (gravity comparisons, airlock demonstrations)
- Guided tours with different camera angles

**Success Looks Like:**
- Professional educational quality
- Innovative teaching methods
- Multiple ways to explore and learn

**Perfect for:** Creating museum-quality educational experiences!

### Slide 9: Plenary
**WHAT WE'VE ACHIEVED TODAY:**
- 🎓 Created complete educational experiences about space exploration
- 📚 Combined construction, programming, and teaching skills
- 🚀 Built learning tools that teach real space science
- 👨‍🏫 Became educators who can teach others

**KEY LEARNING:** You've taken basic building components and created sophisticated learning environments that could actually help train future astronauts! You're now space education experts!

### Slide 10: Next Steps
**PROJECT COMPLETE - WELL DONE!**

**What You've Mastered:**
- 🏗️ **Construction Skills:** Logical base design using modular components
- 🤖 **Programming Skills:** Interactive systems with buttons, doors, and physics
- 🎓 **Educational Design:** Information systems that teach real space science

**Real-World Connections:**
- Your airlock systems work like those on the International Space Station
- Your gravity settings match actual lunar conditions (1/6th Earth gravity)
- Your modular base design reflects real space habitat planning

**You've become Space Engineers, Programmers, AND Educators!**