# Mission to Mars Coding Unit - Complete Slide Content

## TITLE SLIDE
**Title:** Mission to Mars Coding Unit
**Subtitle:** Year 5 • 6 weeks • Ages 10-11
Building Interactive Mars Bases Through Code

---

# LESSON 1: SOLAR SYSTEM ANIMATION

## SLIDE 1 - LESSON 1 TITLE
**Title:** Lesson 1: Solar System Animation
**Subtitle:** Making planets move in space

## SLIDE 2 - LEARNING OBJECTIVES
**Title:** What We'll Learn Today

**Content:**
• Make planets move in circles that never stop
• Make lots of planets move at the same time
• Make close planets move faster than far planets

**Key Words:** Paths, Forever Loops, Parallel Processing

## SLIDE 3 - CODE STRUCTURE
**Title:** The Code We'll Use

**Content:**
```
when play clicked
run parallel
    forever
        move Earth on path earth_path forward in 10 sec
run parallel
    forever
        move Moon on path moon_path forward in 3 sec
```

**Steps to Build:**
1. Create circular paths for each planet
2. Close planets = shorter times, far planets = longer times
3. Use "run parallel" so all planets move together

## SLIDE 4 - REAL LIFE EXAMPLES
**Title:** It's Like Real Life!

**Content:**
🚂 **Paths** = Train tracks
Trains follow the same route every time

🎡 **Forever loops** = Ferris wheel
It keeps spinning and never stops

🎺 **Parallel processing** = School band
Everyone plays at the same time

🏎️ **Different speeds** = Cars on motorway
Fast cars overtake slow cars

## SLIDE 5 - CHALLENGE LEVELS
**Title:** Your Challenges

**Content:**
🌟 **Easy:** Sun, Earth, Moon (3 objects)
Make Earth go around Sun, Moon go around Earth

⭐⭐ **Medium:** Add more planets (5-6 total)
Add Mercury, Venus, Mars with different speeds

⭐⭐⭐ **Hard:** All 8 planets plus spinning
Make planets spin as they orbit

## SLIDE 6 - CHECK YOUR WORK
**Title:** Mini Check-Up

**Content:**
Talk to your partner:
• Do your planets move without stopping?
• Are close planets faster than far ones?
• What happens when you change the numbers?

---

# LESSON 2: ASTRONAUT CONTROL

## SLIDE 7 - LESSON 2 TITLE
**Title:** Lesson 2: Astronaut Control
**Subtitle:** Moving astronauts through space

## SLIDE 8 - LEARNING OBJECTIVES
**Title:** What We'll Learn Today

**Content:**
• Control how fast objects move using velocity
• Create on/off switches with true/false buttons
• Build smart toggle systems

**Key Words:** Velocity, Boolean Variables, If/Else Logic

## SLIDE 9 - CODE STRUCTURE
**Title:** Movement Code

**Content:**
```
when Up is clicked
    push Astronaut up with velocity 1

when box is clicked
    if gravity_on = false
        set gravity_on to true
        set gravity pull to 10
    else
        set gravity_on to false
        set gravity pull to 0
```

**Remember:** Always add a STOP button (velocity 0)

## SLIDE 10 - REAL LIFE EXAMPLES
**Title:** It's Like Real Life!

**Content:**
⚽ **Velocity** = Kicking a football
Harder kick = ball goes faster and further

💡 **Boolean** = Light switches
Either ON (true) or OFF (false)

🚦 **If/Else** = Traffic lights
IF green THEN go, ELSE stop

📺 **Toggle** = TV remote
Press once = ON, press again = OFF

## SLIDE 11 - CHALLENGE LEVELS
**Title:** Your Challenges

**Content:**
🌟 **Easy:** 6-direction movement + stop
Up, down, left, right, forward, back, STOP

⭐⭐ **Medium:** Control multiple objects
Astronaut, tools, equipment with different speeds

⭐⭐⭐ **Hard:** Smart toggle systems
Buttons that remember on/off states and change colors

---

# LESSON 3: GRAVITY CONTROL ROOM

## SLIDE 12 - LESSON 3 TITLE
**Title:** Lesson 3: Gravity Control Room
**Subtitle:** Organizing lots of objects

## SLIDE 13 - LEARNING OBJECTIVES
**Title:** What We'll Learn Today

**Content:**
• Organize multiple objects using lists
• Create reusable code blocks called functions
• Make objects bounce off walls realistically

**Key Words:** Functions, Lists, Collision Detection

## SLIDE 14 - CODE STRUCTURE
**Title:** Organization Code

**Content:**
```
create empty list gravity_items
add [Light Object] to gravity_items
add [Heavy Object] to gravity_items

define function toggle_gravity()
    for each element in gravity_items
        if gravity_on = true
            set gravity pull to 10
        else
            set gravity pull to 0
```

## SLIDE 15 - REAL LIFE EXAMPLES
**Title:** It's Like Real Life!

**Content:**
📝 **Functions** = Recipe instructions
Write once, use many times for same result

🛒 **Lists** = Shopping lists
Multiple items grouped together

🚗 **Collision** = Bumper cars
Objects bounce off instead of going through

🪶 **Weights** = Feather vs stone
Heavy objects behave differently

## SLIDE 16 - CHALLENGE LEVELS
**Title:** Your Challenges

**Content:**
🌟 **Easy:** Control multiple objects with lists
One button affects many objects

⭐⭐ **Medium:** Light vs heavy physics
Light objects bounce more, heavy ones less

⭐⭐⭐ **Hard:** Smart collision systems
Objects behave differently based on weight

---

# LESSON 4: MARS BASE DESIGN

## SLIDE 17 - LESSON 4 TITLE
**Title:** Lesson 4: Mars Base Design
**Subtitle:** Building your Mars world

## SLIDE 18 - LEARNING OBJECTIVES
**Title:** What We'll Learn Today

**Content:**
• Combine all your coding skills together
• Create camera tours that show off your base
• Design realistic Mars environments

**Key Words:** Integration, Camera Paths, Interactive Objects

## SLIDE 19 - CODE STRUCTURE
**Title:** Base Building Code

**Content:**
```
when Tour_Button is clicked
    move Camera on path tour_path forward in 20 sec

when Airlock_Door is clicked
    call function open_door()
    wait 3 sec
    call function close_door()
```

**Plan Your Base:**
1. Different areas (home, lab, garage)
2. Red Mars landscape
3. Use all previous lessons together

## SLIDE 20 - REAL LIFE EXAMPLES
**Title:** It's Like Real Life!

**Content:**
🧱 **Integration** = Building LEGO
Combine pieces to make something amazing

🎢 **Camera paths** = Theme park ride
Follow route to see different scenes

🏛️ **Interactive objects** = Museum buttons
Touch to make something happen

🎧 **Tours** = Audio guides
Show visitors highlights in order

## SLIDE 21 - CHALLENGE LEVELS
**Title:** Your Challenges

**Content:**
🌟 **Easy:** Basic base (2-3 areas)
Dome, landing pad, rover with simple tour

⭐⭐ **Medium:** Interactive base (4-5 areas)
Habitat, lab, greenhouse with longer tours

⭐⭐⭐ **Hard:** Complex systems (6+ areas)
Multiple tour options and special features

---

# LESSON 5: SHOWCASE AND ASSESSMENT

## SLIDE 22 - LESSON 5 TITLE
**Title:** Lesson 5: Showcase Time
**Subtitle:** Show off your amazing work!

## SLIDE 23 - LEARNING OBJECTIVES
**Title:** What We'll Do Today

**Content:**
• Show your Mars base to others
• Give helpful feedback to classmates
• Think about what you learned

**Key Words:** Presentation, Feedback, Reflection

## SLIDE 24 - SHOWCASE ACTIVITIES
**Title:** How to Showcase

**Content:**
🎥 **Project Tour** (5 minutes each)
Record tour highlighting your best features

👥 **Peer Feedback**
Use feedback forms to help classmates

🤔 **Reflection Questions**
- What was most challenging?
- How did you fix problems?
- What would you add next?

## SLIDE 25 - ASSESSMENT LEVELS
**Title:** How We'll Judge Success

**Content:**
🌟 **Good Work:** Basic features work
Animation, movement, interaction all function

⭐⭐ **Great Work:** Creative combinations
Multiple features working together creatively

⭐⭐⭐ **Amazing Work:** Innovation beyond requirements
Exceptional creativity with technical mastery

## SLIDE 26 - FINAL CELEBRATION
**Title:** Coding Superpowers Unlocked!

**Content:**
🎉 **You Now Have 7 Coding Superpowers:**
• Making moving systems
• Controlling objects
• Organizing complex code
• Simulating physics
• Building interactive worlds
• Solving problems independently
• Thinking like a programmer

**Use these skills everywhere:** Science projects, design challenges, storytelling!

---

# VOCABULARY CHECKLIST

## SLIDE 27 - TECHNICAL WORDS
**Title:** Coding Words You Now Know

**Content:**
**Basic Concepts:**
• Paths - Routes objects follow
• Velocity - Force that moves objects  
• Boolean - True/false switches

**Advanced Concepts:**
• Functions - Reusable code blocks
• Lists - Collections of objects
• Collision - Objects bouncing off boundaries

**Logic Concepts:**
• Conditional - If/else decision making
• Loops - Repeating code blocks
• Integration - Combining multiple skills

---

# BONUS: EDUCATIONAL QUIZZES

## SLIDE 28 - BONUS LESSON
**Title:** Bonus: Mars Quiz Systems
**Subtitle:** Make your base educational too!

## SLIDE 29 - QUIZ OBJECTIVES
**Title:** Adding Learning Games

**Content:**
• Create questions that respond to answers
• Give helpful hints for wrong answers
• Make learning fun and interactive

**Sample Mars Questions:**
• What gas makes up most of Mars atmosphere?
• How much would you weigh on Mars?
• What's the average temperature on Mars?

## SLIDE 30 - QUIZ CODE
**Title:** Smart Quiz Code

**Content:**
```
when Quiz_Button is clicked
    if text of Answer_Input = "carbon dioxide"
        say "Correct! Mars atmosphere is 95% CO2"
        show object Reward_Item
    else
        say "Not quite - think about greenhouse gases!"
```

**Make Good Quizzes:**
1. Choose interesting Mars facts
2. Give helpful hints for wrong answers
3. Celebrate correct answers