from utils import type_text, slow_print, get_choice, CYAN, YELLOW, RED, GREEN, WHITE, BOLD, RESET, clear_screen
from models import Enemy

class Scene:
    def __init__(self, description, choices=None, enemy=None, narrative_after=None):
        self.description = description
        self.choices = choices or [] # List of dicts: {"text": str, "redemption": int, "brotherhood": int, "despair": int, "next_scene": str}
        self.enemy = enemy
        self.narrative_after = narrative_after

class Chapter:
    def __init__(self, title, scenes):
        self.title = title
        self.scenes = scenes # Dict mapping scene_id to Scene object

def get_story_data():
    story = {}

    # CHAPTER 1: THE DAYS OF LIGHT
    story[1] = Chapter("The Days of Light", {
        "start": Scene(
            "The air in the Arctis valley is heavy with the scent of amber-grass and untroubled memory. "
            "Kael, you stand amidst the waist-high gold, your wooden blade a poor imitation of the destiny you carry. "
            "Beside you, Darius breathes in sharp, jagged rhythms, his eyes already fixed on a horizon you cannot yet see.",
            [
                {"text": "'The world feels... fragile today, Darius.'", "brotherhood": 1, "next_scene": "father_joins"},
                {"text": "'Focus on the strike, Darius. Not the horizon.'", "brotherhood": -1, "next_scene": "father_joins"}
            ]
        ),
        "father_joins": Scene(
            "Your father approaches, his steps silent as the passage of time. "
            "'Power is not the right to bend fate, my sons,' he says, his voice a warm resonance. "
            "'It is the duty to bear its weight.'",
            [
                {"text": "Bow respectfully. 'We are ready to learn.'", "brotherhood": 2, "next_scene": "training_fight"},
                {"text": "Grip your blade. 'I want to hold the wheel myself.'", "brotherhood": -2, "next_scene": "training_fight"}
            ]
        ),
        "training_fight": Scene(
            "The Father steps into the tall grass. 'Then let us see your resolve.'",
            enemy=Enemy("The Father (Memory Echo)", 80, 10, 5, 12, 10, 150, gold_reward=20, rank="F", is_boss=True),
            narrative_after="'Strength is a tool, Kael. Do not forget who it serves.'",
            choices=[{"text": "Rest before the sun sets.", "next_scene": "day_end"}]
        ),
        "day_end": Scene(
            "The sun dips below the Arctis peaks, casting long, violet shadows. Darius looks at his hands, trembling slightly.",
            [{"text": "Proceed toward the Fracture.", "next_scene": "end"}]
        )
    })

    # CHAPTER 2: THE SHADOW FALLS
    story[2] = Chapter("The Shadow Falls", {
        "start": Scene(
            "The valley is no longer gold. It is ash. The Arctis home is a hollow ribcage of timber and smoke.",
            [{"text": "Search for survivors.", "next_scene": "remnant_fight"}]
        ),
        "remnant_fight": Scene(
            "A Refracted Remnant—a creature of static and sorrow—emerges from the ruin.",
            enemy=Enemy("Refracted Remnant", 150, 15, 8, 15, 5, 300, gold_reward=50, rank="E"),
            narrative_after="The creature shatters into charcoal dust.",
            choices=[{"text": "Find Darius.", "next_scene": "the_confrontation"}]
        ),
        "the_confrontation": Scene(
            "Darius stands over your father's remains. A dark pulse emanates from him.",
            [
                {"text": "'Darius, stop! This isn't the way!'", "brotherhood": 3, "next_scene": "darius_leaves"},
                {"text": "Witness the darkness in silence.", "brotherhood": -2, "next_scene": "darius_leaves"}
            ]
        ),
        "darius_leaves": Scene(
            "Darius vanishes into a rift, leaving a grey feather behind.",
            narrative_after="You feel a cold weight in your chest. The path is set."
        )
    })

    # CHAPTER 3: THE WORLD UNRAVELS
    story[3] = Chapter("The World Unravels", {
        "start": Scene(
            "You traverse the Floating Spires. Gravity is a choice, and today, it chooses poorly.",
            [
                {"text": "Scale the Obsidian Spire.", "next_scene": "spire_fight"},
                {"text": "Search the ruins for Ether-Drops.", "next_scene": "search_loot"}
            ]
        ),
        "search_loot": Scene(
            "You find a forgotten cache. (Gained 1 Ether-Drop)",
            narrative_after="The air feels thinner here.",
            choices=[{"text": "Climb the spire anyway.", "next_scene": "spire_fight"}]
        ),
        "spire_fight": Scene(
            "A Chrono-Sentinel guards the passage—it moves in staccato bursts of speed.",
            enemy=Enemy("Chrono-Sentinel", 250, 25, 15, 30, 15, 1000, gold_reward=150, rank="D"),
            narrative_after="The machine grinds to a halt.",
            choices=[{"text": "Proceed to the rift's heart.", "next_scene": "rift_heart"}]
        ),
        "rift_heart": Scene(
            "The distortion here is immense. You can feel Darius's rage as a physical pressure.",
            choices=[
                {"text": "Face the Time Phantom.", "next_scene": "phantom_fight"},
                {"text": "Return to Ethereal Camp (Heal/Shop).", "next_scene": "camp", "return_scene": "rift_heart"},
                {"text": "Take a moment to farm memories (Repeat).", "next_scene": "start"}
            ]
        ),
        "phantom_fight": Scene(
            "The Phantom wails, a vortex of half-lived lives.",
            enemy=Enemy("Time Phantom", 400, 35, 20, 25, 20, 2500, gold_reward=300, rank="C", is_boss=True),
            narrative_after="The phantom dissolves. You are reaching the threshold."
        )
    })

    # CHAPTER 4: THE FATE NEXUS
    story[4] = Chapter("The Fate Nexus", {
        "start": Scene(
            "The sky is a jagged mosaic of lavender and obsidian. Darius waits upon a throne of glass.",
            choices=[
                {"text": "Approaching with an open heart. 'Brother...'", "brotherhood": 10, "next_scene": "nexus_guard"},
                {"text": "Approach with a drawn blade. 'Traitor...'", "brotherhood": -10, "next_scene": "nexus_guard"}
            ]
        ),
        "nexus_guard": Scene(
            "Before you reach him, the Herald of Despair blocks your path.",
            enemy=Enemy("Herald of Despair", 800, 50, 30, 40, 25, 5000, gold_reward=500, rank="B"),
            narrative_after="The Herald falls, its cry echoing into the void.",
            choices=[{"text": "Challenge Darius.", "next_scene": "boss_1"}]
        ),
        "boss_1": Scene(
            "Darius (The Mournful) strikes. Phase 1: The Weight of Loss.",
            enemy=Enemy("Darius (The Mournful)", 1200, 65, 40, 50, 30, 10000, gold_reward=1000, rank="A", is_boss=True),
            narrative_after="He staggers, but the Feather glows with a terrifying intensity."
        )
    })
    
    # CHAPTER 5: THE FINAL MERCY
    story[5] = Chapter("The Final Mercy", {
        "start": Scene(
            "Final Phase. Reality dissolves. Darius has become the engine of the Unraveling.",
            enemy=Enemy("Darius (Heart of the Rift)", 2500, 85, 50, 70, 50, 0, gold_reward=5000, rank="S", is_boss=True),
            narrative_after="It is over. One way or another."
        )
    })

    return story
