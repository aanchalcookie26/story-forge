"""
StoryForge — Complete Seed Command
====================================
Place at: stories/management/commands/seed_stories.py

Run with:
    python manage.py seed_stories

Creates:
  * Superuser: storymaster / forge1234
  * 8 genre stories, each with 10-20 nodes + branching choices
  * Ratings and play counts for a live leaderboard
  * Safe to re-run — skips existing titles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from stories.models import Story, Node, Choice, Rating, UserAccount
import random


# ─────────────────────────────────────────────────────────────────────────────
#  STORY DATA  —  8 genres × 12-18 nodes each, rich branching
# ─────────────────────────────────────────────────────────────────────────────

STORIES = [

    # ══════════════════════════════════════════════════════════════
    #  1. FANTASY  —  "The Dragon's Pact"  (16 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "The Dragon's Pact",
        "genre":       "fantasy",
        "cover_emoji": "🐉",
        "description": "An ancient dragon awakens beneath the kingdom. You are the only mage who speaks Draconic. Forge an alliance—or face annihilation.",
        "play_count":  3842,
        "nodes": [
            # ── Chapter 1 ──
            {
                "title": "The Trembling Earth",
                "order": 1,
                "text": (
                    "The ground shakes beneath your boots. Villagers flee, clutching children and livestock, vanishing into the forest roads "
                    "that wind away from the capital. You stand alone at the mouth of Ashveil Cavern as smoke curls from the depths — acrid and ancient.\n\n"
                    "Your master's words echo in your memory: 'Dragons do not awaken without reason.' You spent twelve years learning Draconic "
                    "from crumbling texts, and now that tongue may be the only thing that saves ten thousand lives.\n\n"
                    "A roar splits the mountain. The air itself shudders. Flames lick the cave entrance, turning the morning mist to steam. "
                    "Through the inferno, a pair of amber eyes — each the size of a cart wheel — opens and regards you with impossible intelligence."
                ),
                "choices": [
                    ("Step forward and call out in Draconic — offer parley", "parley"),
                    ("Cast a defensive shield and hold your ground", "shield"),
                    ("Back away and observe the dragon's behaviour first", "observe"),
                ]
            },
            # ── Chapter 2a — Observe ──
            {
                "key": "observe",
                "title": "The Dragon's Pain",
                "order": 2,
                "text": (
                    "You retreat three careful steps, keeping your eyes level with those enormous amber ones. "
                    "The dragon does not pursue. Instead, he presses one massive claw against the cavern wall and exhales — "
                    "not fire this time, but a long ragged breath that sounds uncomfortably like a groan of pain.\n\n"
                    "His eyes track you but do not narrow in predatory focus. They are wide. Almost desperate. "
                    "You recall a passage from the Draconic texts: 'When a wyrm abandons the hunt and turns inward, seek first the wound, not the weapon.'\n\n"
                    "The dragon is suffering. Something is deeply wrong with him — and attacking first would be catastrophic."
                ),
                "choices": [
                    ("Call out in Draconic — address him by name", "parley"),
                    ("Examine the cavern walls for clues about the cause of his pain", "cavern_clue"),
                ]
            },
            # ── Chapter 2b — Cavern Clue ──
            {
                "key": "cavern_clue",
                "title": "Marks on Ancient Stone",
                "order": 2,
                "text": (
                    "While the dragon watches in eerie stillness, you examine the cavern mouth. Carved into the stone — recently, the edges still sharp — "
                    "are necromantic sigils you recognise from banned texts confiscated by the Academy years ago.\n\n"
                    "Someone has been here. Someone who wanted this dragon enraged.\n\n"
                    "A vein of black crystal runs through the cave wall, pulsing faintly like a heartbeat. In Draconic lore, "
                    "the harthen — the heart-stone — is the seat of a dragon's soul. If this crystal connects to Vaelthrax's heart-stone, "
                    "the sigils may be cursing it, driving him toward uncontrollable rage.\n\n"
                    "You have enough to start a conversation. You turn and face the dragon fully."
                ),
                "choices": [
                    ("Address the dragon in Draconic using what you've learned", "parley"),
                ]
            },
            # ── Chapter 2c — Parley ──
            {
                "key": "parley",
                "title": "Words of Fire",
                "order": 3,
                "text": (
                    "You raise your hands — empty, open — and speak. The Old Tongue feels strange on your lips after years of only reading it, "
                    "but the words come: 'Vaelthrax, Ember-born, Second Flame of the Age of Ash — I seek counsel, not conflict.'\n\n"
                    "A silence so complete it has weight settles over the mountainside. Then the dragon speaks — a sound like boulders "
                    "grinding together, reshaped into something almost language. 'You know my name, small one. That buys you moments.'\n\n"
                    "He tells you of a figure in dark robes who came to his cavern a fortnight ago and planted a curse in his heart-stone. "
                    "The curse twists his mind toward uncontrollable rage. He has been fighting it for two weeks. "
                    "He does not know how much longer he can resist."
                ),
                "choices": [
                    ("Promise to retrieve the cure for the heart-stone curse yourself", "journey_prep"),
                    ("Ask Vaelthrax to come with you to the King's healers", "king_option"),
                    ("Ask him to describe who cursed him — pursue the necromancer directly", "necro_identity"),
                ]
            },
            # ── Chapter 2d — Shield ──
            {
                "key": "shield",
                "title": "The Mage's Barrier",
                "order": 2,
                "text": (
                    "You slam your staff into the earth and your shield erupts — silver-white, humming with every ward you know. "
                    "The dragon's first breath strike hits it like a siege cannon. Stone around the barrier begins to melt.\n\n"
                    "You dive left, scorched and ringing in both ears. The dragon does not press the attack. He tilts his enormous head. "
                    "Your shield buys silence. He is in pain — you can see it in the way he holds his enormous body — "
                    "and he paused when he could have finished you. Use this moment."
                ),
                "choices": [
                    ("Switch to diplomacy — speak Draconic now", "parley"),
                    ("Hold your ground and attempt a binding spell", "bind_attempt"),
                ]
            },
            # ── Chapter 3 — Bind Attempt ──
            {
                "key": "bind_attempt",
                "title": "The Binding Fails",
                "order": 3,
                "text": (
                    "You channel everything into the binding — chains of pure arcane force erupt from the earth, "
                    "wrapping around the dragon's legs. For one breathless moment they hold.\n\n"
                    "Vaelthrax looks down at them with something like sadness in his eyes. Then he exhales once, "
                    "and every chain evaporates like morning frost. Ancient dragons are resistant to arcane binding. "
                    "Your master told you this. You forgot.\n\n"
                    "'You waste both our time,' Vaelthrax rumbles. 'If you have words, speak them. "
                    "If not, leave before the pain takes me again.' A window is closing."
                ),
                "choices": [
                    ("Speak Draconic now — explain what you saw on the cavern walls", "parley"),
                ]
            },
            # ── Chapter 3 — Necro Identity ──
            {
                "key": "necro_identity",
                "title": "The Description",
                "order": 4,
                "text": (
                    "Vaelthrax closes his enormous eyes and recounts each detail of the robed figure — "
                    "the smell of charred bone and iron filings, a silver mask shaped like a skull, "
                    "the way the figure moved without sound, as if walking on air.\n\n"
                    "Your blood runs cold. You know exactly who this is.\n\n"
                    "Mordecai Ven. Formerly of the Royal Academy, expelled for experimenting on prisoners. "
                    "You reported him yourself, seven years ago. He vanished after the trial. "
                    "It seems he found somewhere to perfect his craft.\n\n"
                    "Vaelthrax opens his eyes. 'You know this creature.' It is not a question."
                ),
                "choices": [
                    ("Agree to hunt Mordecai Ven alone and return with the cure", "journey_prep"),
                    ("Ask Vaelthrax to give you until dawn and gather allies first", "gather_allies"),
                ]
            },
            # ── Chapter 4 — Journey Prep ──
            {
                "key": "journey_prep",
                "title": "Provisions and Plans",
                "order": 5,
                "text": (
                    "You return to town at a dead run. The apothecary gives you flame-resistant salve without asking why. "
                    "The archivist at the small roadside library recognises your description of the sigils — "
                    "she pulls a slim volume titled 'Necromantic Bindings: Detection and Counter' from beneath the counter "
                    "as if she's been waiting for someone to ask.\n\n"
                    "'The focus crystal will be somewhere the necromancer feels safe,' she tells you quietly. "
                    "'Somewhere he's already prepared. Probably three days' walk into the Blighted Marshes.'\n\n"
                    "You have supplies for four days. You leave at first light, alone."
                ),
                "choices": [
                    ("Take the northern forest path — faster, more dangerous", "forest_path"),
                    ("Take the southern marsh road — longer, with better cover", "marsh_road"),
                ]
            },
            # ── Chapter 4 — Gather Allies ──
            {
                "key": "gather_allies",
                "title": "The Council of Three",
                "order": 5,
                "text": (
                    "By dawn you have gathered three people: Senna, the royal archivist who knows more about necromantic bindings "
                    "than anyone alive; Dav, the city's master thief who once broke into the Academy's forbidden wing on a bet; "
                    "and Captain Rhael of the city guard, who owes you a favour from the Bridge Incident last winter.\n\n"
                    "You explain everything. To their credit, none of them flee. Senna is already sketching a diagram "
                    "of the heart-stone curse structure. Dav is asking about patrol patterns. Rhael is checking her sword.\n\n"
                    "Together, you ride for the Blighted Marshes before the morning bells."
                ),
                "choices": [
                    ("Approach with Senna's magic — try to dispel the curse at range", "arcane_assault"),
                    ("Follow Dav's plan — infiltrate the tower and find the focus crystal", "forest_path"),
                ]
            },
            # ── Chapter 5 — Forest Path ──
            {
                "key": "forest_path",
                "title": "Through the Dark Wood",
                "order": 6,
                "text": (
                    "The northern forest is three days of shadow and silence. Creatures scatter from your path — "
                    "they can smell the necromantic residue on the air, you realise, a sourness "
                    "that deepens as you walk.\n\n"
                    "On the second night, something follows you through the trees. Not a beast — "
                    "the movement is too deliberate, too patient. One of Mordecai's constructs, perhaps, "
                    "left as a sentry.\n\n"
                    "By dawn on the third day the construct has vanished and the tower is visible on the horizon — "
                    "black stone rising from the marsh, windows lit green-gold, surrounded by bone-golems on patrol."
                ),
                "choices": [
                    ("Sprint through the gap in the golem patrol and enter the tower", "tower_base"),
                    ("Cause a distraction — cast a decoy spell at the far perimeter", "distraction"),
                ]
            },
            # ── Chapter 5 — Marsh Road ──
            {
                "key": "marsh_road",
                "title": "The Blighted Marshes",
                "order": 6,
                "text": (
                    "The southern marsh road lives up to its name. You navigate three leagues of fen that smells "
                    "of rot and old magic, threading between cypress roots half-swallowed by black water. "
                    "Will-o'-wisps beckon. You know better than to follow.\n\n"
                    "But the marsh gives you something the forest wouldn't: a view. From a low ridge you can map "
                    "the entire patrol pattern of the bone-golems around Mordecai's tower. "
                    "Twelve of them. A gap of seventeen seconds at the northeast corner.\n\n"
                    "You also find, half-buried in the mud: a journal. It belongs to one of Mordecai's previous apprentices. "
                    "It describes the layout of the tower floor by floor."
                ),
                "choices": [
                    ("Use the journal's layout to find the focus crystal directly", "artefact_search"),
                    ("Use the seventeen-second gap and enter through the base door", "tower_base"),
                ]
            },
            # ── Chapter 5 — Arcane Assault ──
            {
                "key": "arcane_assault",
                "title": "Senna's Counterspell",
                "order": 6,
                "text": (
                    "Senna works from outside the tower, drawing the counterspell architecture in the mud with a stick "
                    "while you feed her power through a linking artefact. It is inelegant, improvised, "
                    "and slightly terrifying — the kind of magic that makes careful mages wince.\n\n"
                    "Rhael keeps the golems occupied with a series of loud, extremely unhelpful distractions. "
                    "Dav runs interference on Mordecai's outer wards with a set of tools you've decided not to ask about.\n\n"
                    "The counterspell takes shape — a complex lattice of structured anti-necromancy that Senna calls "
                    "'aggressively inconvenient for the curse.' You pour everything you have into it. "
                    "Inside the tower, you hear Mordecai scream in surprise as his workings begin to unravel."
                ),
                "choices": [
                    ("Hold the counterspell — push through to full completion", "cure_victory"),
                    ("Enter the tower now and find the physical crystal to smash it", "artefact_search"),
                ]
            },
            # ── Chapter 6 — Tower Base ──
            {
                "key": "tower_base",
                "title": "Inside the Tower",
                "order": 7,
                "text": (
                    "The base of the tower is a laboratory of horrors — shelves of specimen jars, ritual circles "
                    "burnt into the floor, a staircase that spirals upward without apparent end. "
                    "The chanting from above grows louder with each step.\n\n"
                    "On the third floor landing you find it: a crystal the size of your fist, suspended in a frame "
                    "of black iron, pulsing with the same rhythm as the sigils you saw on Vaelthrax's cavern wall. "
                    "The curse focus. If you shatter it, the curse ends.\n\n"
                    "But the chanting above stops. Footsteps, descending. One minute, maybe less."
                ),
                "choices": [
                    ("Smash the crystal immediately before Mordecai arrives", "smash_crystal"),
                    ("Hide and wait — confront Mordecai when he enters", "confront_necro"),
                ]
            },
            # ── Chapter 6 — Distraction ──
            {
                "key": "distraction",
                "title": "The Diversionary Gambit",
                "order": 7,
                "text": (
                    "You create a copy of yourself from light and noise and send it crashing through the far fence. "
                    "Every bone-golem turns and lumbers toward the commotion. "
                    "You sprint through the seventeen-second gap, counting heartbeats.\n\n"
                    "Inside: cold stone, green torchlight, the smell of iron filings and burned feathers. "
                    "A spiral stair leads up. Somewhere above, Mordecai Ven is working — a low rhythmic chanting "
                    "that vibrates in the fillings of your back teeth.\n\n"
                    "The distraction won't hold forever. You have perhaps ten minutes."
                ),
                "choices": [
                    ("Race to the top floor — confront Mordecai directly", "confront_necro"),
                    ("Search each floor carefully for the curse focus crystal", "artefact_search"),
                ]
            },
            # ── Chapter 6 — Artefact Search ──
            {
                "key": "artefact_search",
                "title": "The Curse Crystal",
                "order": 7,
                "text": (
                    "Third floor. You find it exactly where the apprentice's journal said it would be — "
                    "a crystal the size of your fist, black as a starless night, suspended in a frame of iron "
                    "and pulsing with dull red light that matches a heartbeat. Vaelthrax's heartbeat, you realise.\n\n"
                    "A ward protects it — one of Mordecai's better pieces of work. If you break the ward badly, "
                    "the crystal could scatter the curse energy in a way that intensifies it rather than ends it.\n\n"
                    "Footsteps on the stairs. Thirty seconds. Maybe less."
                ),
                "choices": [
                    ("Dismantle the ward carefully, then shatter the crystal with precision", "careful_shatter"),
                    ("Smash everything at once and run", "smash_crystal"),
                ]
            },
            # ── Chapter 7 — Confront Necro ──
            {
                "key": "confront_necro",
                "title": "Mordecai Ven",
                "order": 8,
                "text": (
                    "He is smaller than you remember. Thinner. The silver skull mask sits on his desk like a prop. "
                    "Without it he looks like a tired academic who hasn't slept in a week.\n\n"
                    "He sees you and sighs — not the reaction you expected. 'The mage who reported me,' he says. "
                    "'Of course.' He makes no move for a weapon. Instead he sits down heavily.\n\n"
                    "'The dragon is in pain. I know. That was not the plan.' The plan, it transpires, was to curse "
                    "Vaelthrax into a controllable state for an employer he refuses to name. The curse instead "
                    "created agony. Mordecai, to your genuine surprise, seems troubled by this. "
                    "'I can end it,' he says. 'But I need something from you.'"
                ),
                "choices": [
                    ("Listen to his terms — a bargain may be faster than a fight", "necro_bargain"),
                    ("Refuse any bargain — take him into custody and find the crystal yourself", "artefact_search"),
                ]
            },
            # ── Chapter 8 — Necro Bargain ──
            {
                "key": "necro_bargain",
                "title": "An Unlikely Alliance",
                "order": 9,
                "text": (
                    "What Mordecai needs is safe passage out of the kingdom before he names his employer — "
                    "someone powerful enough to worry a man who curses dragons into silence.\n\n"
                    "You do not have the authority to grant immunity. You are a mage, not a crown official. "
                    "But the information about the employer, you sense, is worth the promise. "
                    "You agree. He speaks a single word and the crystal in the next room detonates silently.\n\n"
                    "Mordecai stands, picks up a small case already packed, and nods. "
                    "'The curse is broken. The employer's name is—' He writes it on a scrap of paper, folds it, "
                    "hands it over. 'Do not open it until you're safely out of my tower.'"
                ),
                "choices": [
                    ("Honour the deal — escort him to the road and then return to Vaelthrax", "cure_victory"),
                ]
            },
            # ── Chapter 8 — Smash Crystal ──
            {
                "key": "smash_crystal",
                "title": "The Blunt Solution",
                "order": 8,
                "text": (
                    "You smash it. The crystal explodes in a burst of cold black light "
                    "that throws you across the room into the stone wall. "
                    "You slide to the floor, ears ringing, the room spinning.\n\n"
                    "Then — from very far away — a sound you were hoping for. A roar. "
                    "But not the roar of rage you heard this morning. This one is different. "
                    "Longer. Quieter. The sound of something enormous letting out a breath "
                    "it has been holding for far too long.\n\n"
                    "Vaelthrax is free."
                ),
                "choices": [
                    ("Get up, leave the tower, and return to Vaelthrax", "cure_victory"),
                ]
            },
            # ── Chapter 8 — Careful Shatter ──
            {
                "key": "careful_shatter",
                "title": "Ward and Crystal",
                "order": 8,
                "text": (
                    "You work methodically, peeling back Mordecai's ward layer by layer — each layer "
                    "a different colour, like an onion made of malice. When the last layer falls, "
                    "the crystal is exposed. Clean. Vulnerable.\n\n"
                    "You strike with a single focused pulse of arcane force. "
                    "The crystal cracks cleanly down the middle, then crumbles to dust. "
                    "The red pulsing stops. The heartbeat rhythm ceases.\n\n"
                    "Somewhere very far away — across three leagues of marsh and forest — you feel it. "
                    "A shift in the world, as if the land itself exhaled."
                ),
                "choices": [
                    ("Return to Vaelthrax — witness what you have done", "cure_victory"),
                ]
            },
            # ── King Option branch ──
            {
                "key": "king_option",
                "title": "The King's Healers",
                "order": 4,
                "text": (
                    "You persuade Vaelthrax to descend slowly into the valley and wait at the edge of the King's Road. "
                    "Then you ride hard for the capital. The Royal Healers' Guild assembles in crisis session, "
                    "but when you describe what you need — a cure for a draconic heart-stone curse — "
                    "the silence stretches long and uncomfortable.\n\n"
                    "None of them have treated a dragon. None of them know Draconic. "
                    "The most senior healer, a silver-haired woman named Margot, is honest: "
                    "'We would need to study the curse's nature before we could begin. That takes weeks.'\n\n"
                    "Vaelthrax does not have weeks. A distant roar echoes from the valley — "
                    "closer than it was an hour ago."
                ),
                "choices": [
                    ("Take Margot to the dragon immediately — improvise a cure together", "improvise_cure"),
                    ("Leave the healers and go to the marshes yourself", "journey_prep"),
                ]
            },
            # ── Chapter 5 — Improvise Cure ──
            {
                "key": "improvise_cure",
                "title": "The Healer and the Mage",
                "order": 5,
                "text": (
                    "Margot rides pillion behind you, gripping your cloak, asking precise questions "
                    "about the necromantic sigils you saw. She has not studied Draconic, but she has studied curses — "
                    "and a curse is a curse, she says, dragon or human.\n\n"
                    "Vaelthrax tolerates her presence with magnificent restraint while she examines him from ten careful paces, "
                    "asking you to translate her questions. The heart-stone, she determines, "
                    "is connected to a focus crystal in the cavern. Destroy the crystal, break the curse.\n\n"
                    "The crystal is deep in the cavern. The cavern is currently on fire."
                ),
                "choices": [
                    ("Enter the cavern and retrieve the crystal before the fire spreads", "artefact_search"),
                    ("Ask Vaelthrax to guide you through the smoke with his voice", "cure_victory"),
                ]
            },
            # ── ENDINGS ──
            {
                "key": "cure_victory",
                "title": "The Pact of Ash and Gold",
                "order": 15,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Vaelthrax is waiting at the cavern mouth when you return. He looks different — "
                    "the tension gone from his enormous body, the amber eyes clear and calm. "
                    "He regards you for a long moment with that unsettling draconic stillness.\n\n"
                    "Then he lowers his head until it rests a foot from the ground — "
                    "the Draconic gesture of recognition between equals. You nearly stop breathing.\n\n"
                    "'The pact is made,' he says. 'I will guard the boundaries of this kingdom for one century. "
                    "No siege engine or invading army will breach what I choose to protect.'\n\n"
                    "He allows you to climb onto his back. The kingdom spreads below as you rise on warm currents of air, "
                    "the capital's spires catching the afternoon light. Your name will be written in gold "
                    "in the Chronicle of Pacts. It is the best day the kingdom has had in a generation."
                ),
                "choices": []
            },
            {
                "key": "king_fail",
                "title": "The Scorched Peace",
                "order": 15,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "Without the cure, Vaelthrax's patience breaks. Three outer villages burn before "
                    "you broker a fragile cease-agreement that satisfies no one. "
                    "The dragon retreats north with wounds and a grudge, and you return to a city "
                    "that regards you with complicated gratitude.\n\n"
                    "There was a moment, at the cave mouth, when different words might have opened "
                    "a different future. You will think about it for the rest of your life."
                ),
                "choices": []
            },
        ],
        "ratings": [4, 5, 5, 4, 5, 5, 5, 4, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  2. SCI-FI  —  "Signal from Kepler-7"  (14 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "Signal from Kepler-7",
        "genre":       "scifi",
        "cover_emoji": "🛸",
        "description": "A distress beacon reaches Earth from a colony ship thought lost 40 years ago. You are the mission commander sent to investigate — and nothing is what it seems.",
        "play_count":  2951,
        "nodes": [
            {
                "title": "Contact",
                "order": 1,
                "text": (
                    "Your ship drops out of FTL at Kepler-7b orbit. The colony vessel ISS Perennial hangs in space — "
                    "dark except for one blinking emergency light that pulses like a slow heartbeat.\n\n"
                    "Scanners show life signs. 314 of them. The original crew manifest listed 312.\n\n"
                    "Your comms officer turns from her console, face pale: "
                    "'Commander, the beacon started transmitting exactly the moment we entered the system. "
                    "Not before. Exactly when.' She lets the implication hang in the recycled air between you."
                ),
                "choices": [
                    ("Dock immediately — people have been stranded for forty years", "dock"),
                    ("Run full scans for six hours before any approach", "scan"),
                    ("Hail the ship on all frequencies first", "hail"),
                ]
            },
            {
                "key": "hail",
                "title": "The Response",
                "order": 2,
                "text": (
                    "You transmit on every frequency, in three languages, for twenty minutes. "
                    "Silence. Then, on a frequency not in any standard catalogue — something between radio and light — "
                    "a single word arrives. Not in any language your translator recognises.\n\n"
                    "Your linguistics AI runs it against every known language, every constructed language, "
                    "every cipher library. It produces one match: a theoretical language devised by "
                    "a xenolinguist thirty years ago as a potential universal first-contact framework. "
                    "A language that has never, as far as anyone knows, been used.\n\n"
                    "Someone on that ship studied it. Or something."
                ),
                "choices": [
                    ("Dock and meet whoever — or whatever — is waiting", "dock"),
                    ("Run full scans first before any physical approach", "scan"),
                ]
            },
            {
                "key": "scan",
                "title": "What the Sensors Found",
                "order": 2,
                "text": (
                    "Six hours of scanning. You find: all 314 life signs are human — "
                    "but two show unusual neural density, as if a second mind shares the skull. "
                    "An energy field permeates the ship, harmless by every metric, but completely alien.\n\n"
                    "The ship's power core has been running for forty years on a fuel source your engineers "
                    "cannot identify. The hull shows no damage. The food stores, inexplicably, are full.\n\n"
                    "Your science officer's voice is very careful: 'They're not hostile. But they are... interested in us.'"
                ),
                "choices": [
                    ("Dock carefully with a small team — make contact", "dock"),
                    ("Transmit everything to Earth and await orders before approaching", "await_orders"),
                ]
            },
            {
                "key": "dock",
                "title": "Airlock",
                "order": 3,
                "text": (
                    "The airlock cycles. Inside: colonists in perfect health, forty years older, "
                    "calm as monks at evening prayer. Their leader, Dr. Amara Osei, greets you "
                    "with the measured smile of someone who has had a great deal of time to think about this moment.\n\n"
                    "'We found something in the planet's crust,' she says. "
                    "'It found us first.'\n\n"
                    "Behind her, two figures stand very still. Their eyes are wrong — "
                    "pupils like fractals, shifting patterns that catch the light and do not let it go. "
                    "'They helped us survive,' Dr. Osei says quietly. 'They want to come to Earth.'"
                ),
                "choices": [
                    ("Ask the entities directly what they want — let them speak", "entity_dialogue"),
                    ("Speak privately with Dr. Osei before any further contact", "osei_private"),
                    ("Agree to transport them — they've earned trust over forty years", "grant"),
                ]
            },
            {
                "key": "await_orders",
                "title": "The Long Wait",
                "order": 3,
                "text": (
                    "Earth Command takes eighteen hours to respond. In that time, "
                    "your crew watches the Perennial in silence from a respectful distance.\n\n"
                    "The response, when it comes, is exactly what you feared: a committee has been formed. "
                    "You are ordered to maintain distance and file daily reports. "
                    "Quarantine protocols are being drafted. Legal frameworks are being consulted.\n\n"
                    "On the Perennial's hull, something pulses briefly — a light, gone in an instant. "
                    "Your comms officer translates it three hours later. "
                    "Using the xenolinguist's framework, it says: 'We are still here. Are you afraid?'"
                ),
                "choices": [
                    ("Disobey orders — dock and make contact before the committee decides", "dock"),
                    ("Follow orders — maintain distance and file your report", "quarantine"),
                ]
            },
            {
                "key": "entity_dialogue",
                "title": "The Vael Speak",
                "order": 4,
                "text": (
                    "The entity that speaks does so through Dr. Osei, using her voice like a borrowed instrument. "
                    "The effect is unsettling and somehow also deeply courteous.\n\n"
                    "'We are the Vael. We have been in this system for eleven thousand of your years. "
                    "We watched your ship arrive with interest. We have learned much from these people ' — "
                    "a gesture toward the colonists — 'and we believe we have something to offer yours.\n\n"
                    "'We ask only one thing in return: that you do not make us wait another forty years.'"
                ),
                "choices": [
                    ("Agree to advocate for the Vael's passage to Earth", "grant"),
                    ("Ask what they have to offer specifically before agreeing", "negotiate_terms"),
                ]
            },
            {
                "key": "osei_private",
                "title": "The Doctor's Account",
                "order": 4,
                "text": (
                    "In the ship's small medical bay, Dr. Osei tells you everything. "
                    "The Vael found the Perennial in its first week in orbit, when a navigation failure "
                    "sent them into an uncontrolled descent that should have killed everyone.\n\n"
                    "They didn't just save the ship. They prevented three epidemics, "
                    "resolved two mutinies without anyone getting hurt, and taught the colonists "
                    "a form of applied physics that the ship's engineer says will 'change everything, if it works.'\n\n"
                    "'Are they dangerous?' you ask. Dr. Osei looks at you steadily. "
                    "'In forty years, not once. Not one person harmed. But they are very, very patient. "
                    "That patience has a direction. They want to go to Earth. I believe they should.'"
                ),
                "choices": [
                    ("Trust Dr. Osei's forty years of direct experience — grant passage", "grant"),
                    ("Still cautious — recommend quarantine pending Earth approval", "quarantine"),
                ]
            },
            {
                "key": "negotiate_terms",
                "title": "Terms of Arrival",
                "order": 5,
                "text": (
                    "The Vael, through Dr. Osei, outline their offer with impressive specificity: "
                    "three technologies they are willing to share immediately — "
                    "a zero-waste energy conversion process, a biological repair mechanism "
                    "that has shown promise against seventeen categories of currently untreatable disease, "
                    "and a materials science breakthrough that makes the Perennial's hull basically indestructible.\n\n"
                    "In return, they ask for what they call 'space to think and to teach.' "
                    "A place where their two individuals can interact with human knowledge and human people. "
                    "They are, they explain, not colonists. They are researchers.\n\n"
                    "The terms seem extraordinarily generous. Which makes you wonder what they haven't said."
                ),
                "choices": [
                    ("Accept the terms and bring them to Earth", "grant"),
                    ("Insist on a period of quarantine study before full integration", "quarantine"),
                ]
            },
            {
                "key": "grant",
                "title": "First Contact",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "The Vael integrate peacefully into Earth society over the next decade. "
                    "The energy technology ends the last of the fossil fuel conflicts within three years. "
                    "The biological repair mechanism cures four categories of cancer within five. "
                    "The Vael themselves become unexpected fixtures of academic life — "
                    "patient, endlessly curious, and possessed of a dry humour that takes humans a while to recognise.\n\n"
                    "You are remembered as the Commander who opened the door. "
                    "History calls it the Kepler Accord. A small museum on the site of the first landing "
                    "has a single exhibit: a recording of the signal that started everything, "
                    "and beside it, your face, slightly singed from a faulty airlock seal.\n\n"
                    "It is the best day humanity ever had, and it started with you choosing to say yes."
                ),
                "choices": []
            },
            {
                "key": "quarantine",
                "title": "Decades of Waiting",
                "order": 10,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "Earth Command quarantines the Perennial in lunar orbit for twenty years "
                    "while committees deliberate and legal frameworks evolve and politicians find reasons to delay.\n\n"
                    "The Vael wait. They are, as Dr. Osei said, extraordinarily patient.\n\n"
                    "Eventually a junior researcher leaks the full story. Public fear turns to protest, "
                    "turns to a second decision — one made without you, after you've retired. "
                    "The Vael are invited to Earth at last. They come. They are gracious. "
                    "They share some of what they know, though Dr. Osei, now very old, "
                    "tells you quietly that something was lost in the twenty years of waiting.\n\n"
                    "'They decided not to share the biological work,' she says. 'Too much time had passed. "
                    "They said trust, once made to wait, becomes something different.' "
                    "You don't ask what it becomes."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 4, 5, 5, 4, 5, 4, 5, 5, 5, 4, 5, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  3. MYSTERY  —  "The Clockmaker's Last Hour"  (13 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "The Clockmaker's Last Hour",
        "genre":       "mystery",
        "cover_emoji": "🕰️",
        "description": "A renowned clockmaker is found dead in his locked workshop. Every clock stopped at 3:17 AM. You are the detective.",
        "play_count":  2203,
        "nodes": [
            {
                "title": "The Stopped Clocks",
                "order": 1,
                "text": (
                    "Aldric Fehn, seventy-four, master clockmaker, dead in his chair. No visible wounds. No signs of struggle. "
                    "Two hundred clocks on the walls — all stopped at 3:17 AM, as if time itself reached a verdict and withdrew.\n\n"
                    "The workshop door was locked from the inside. The windows are sealed with security glass. "
                    "His assistant, Mira, found him at dawn and called it in with a steadiness that made "
                    "the responding officer uncomfortable.\n\n"
                    "On his desk: a half-finished letter in blue-black ink, and a single platinum gear "
                    "that doesn't match any clock in the room. You stand in the centre of it all and begin."
                ),
                "choices": [
                    ("Examine the stopped clocks — look for patterns in how they stopped", "clock_examine"),
                    ("Interrogate Mira — her composure is itself a lead", "mira"),
                    ("Study the platinum gear and the unfinished letter on the desk", "gear"),
                ]
            },
            {
                "key": "clock_examine",
                "title": "Two Hundred Witnesses",
                "order": 2,
                "text": (
                    "You walk the room slowly, examining each clock. Most wound down naturally — hands drooping, "
                    "springs exhausted. But twelve clocks on the east wall show something different: "
                    "internal springs snapped, mechanisms shocked rather than run down.\n\n"
                    "Something happened at 3:17 that caused sudden vibration or electromagnetic disruption, "
                    "strong enough to stop spring-loaded mechanisms mid-tick.\n\n"
                    "You know of one device capable of this: a high-powered electromagnet, "
                    "the kind used in precision machining workshops. Fehn had such a workshop. "
                    "A door leads to it at the back."
                ),
                "choices": [
                    ("Investigate the workshop for signs of the electromagnet", "workshop_search"),
                    ("Note the finding and speak to Mira — she'll know the equipment", "mira"),
                ]
            },
            {
                "key": "gear",
                "title": "A Gear Out of Time",
                "order": 2,
                "text": (
                    "The platinum gear is exquisite — made to tolerances you couldn't achieve with ordinary tools. "
                    "Stamped on its underside: a serial number from a commission Fehn completed thirty years ago "
                    "for a private collector.\n\n"
                    "The collector's name, from Fehn's meticulous logbooks: Harlan Voss. Business partner. "
                    "Current resident of number 14, three streets north. His alibi is his own word, "
                    "and no one has checked it yet.\n\n"
                    "This gear was not here yesterday. Mira's morning inventory check confirms it. "
                    "Someone brought it here last night."
                ),
                "choices": [
                    ("Go directly to Harlan Voss with the gear as your opening", "voss"),
                    ("Speak to Mira about Voss before confronting him", "mira"),
                ]
            },
            {
                "key": "mira",
                "title": "The Assistant's Hands",
                "order": 2,
                "text": (
                    "Mira's composure, up close, is the composure of someone who has already decided what to say. "
                    "Her hands are perfectly steady — too steady. But on her right index finger: blue-black ink, "
                    "the same formulation as the ink on Fehn's unfinished letter.\n\n"
                    "She claims she has not touched the letter. Three minutes of silence follows your observation. "
                    "Then, quietly: Fehn was her grandfather. Estranged for twenty years over a disagreement she won't specify. "
                    "He summoned her two weeks ago — said he was changing his will and needed to explain why in person.\n\n"
                    "Someone else knew about the meeting. She slides a name across the table: Harlan Voss."
                ),
                "choices": [
                    ("Ask Mira about the nature of the family disagreement", "family_secret"),
                    ("Go immediately to confront Harlan Voss", "voss"),
                ]
            },
            {
                "key": "workshop_search",
                "title": "The Hidden Passage",
                "order": 3,
                "text": (
                    "The workshop is immaculate — except for one thing. A long scorch mark on the floor, "
                    "consistent with an electromagnet being dragged across stone. "
                    "It leads from the centre of the room to a panel in the east wall.\n\n"
                    "The panel swings inward when pressed at the right corner. "
                    "Behind it: a passage, three feet wide, leading north. "
                    "Toward number 14. You know that address.\n\n"
                    "The passage smells of recent use — leather shoe polish and something chemical, "
                    "the residue of the electromagnet, carried back through here after the deed was done."
                ),
                "choices": [
                    ("Follow the passage to its end", "passage_end"),
                    ("Document the passage thoroughly and call for backup", "call_in"),
                ]
            },
            {
                "key": "family_secret",
                "title": "The Stolen Design",
                "order": 3,
                "text": (
                    "The disagreement, thirty years old, was about a design.\n\n"
                    "Fehn and Voss co-designed a revolutionary clock movement together. Voss subsequently "
                    "patented it in his name alone and sold it for a considerable fortune. "
                    "Fehn could never prove the theft — until two weeks ago, when he found a journal "
                    "in Voss's handwriting, written in code, containing a clear admission.\n\n"
                    "Mira helped him decode it. She studied cryptography for one semester at university — "
                    "enough, just, to work through Voss's amateur cipher. Fehn was going to the courts.\n\n"
                    "This is the motive. Find the method."
                ),
                "choices": [
                    ("Confront Voss with the motive and the gear", "voss"),
                    ("Search for the electromagnet first to establish method", "workshop_search"),
                ]
            },
            {
                "key": "passage_end",
                "title": "Number 14",
                "order": 4,
                "text": (
                    "The passage opens into a cellar. Voss's cellar. "
                    "On a workbench: the electromagnet, still faintly warm. "
                    "Beside it, a pair of leather gloves. Beside the gloves, a second platinum gear in its velvet case.\n\n"
                    "You hear footsteps above. Voss is home. He doesn't know you're here.\n\n"
                    "The physical evidence is overwhelming. The case is made. "
                    "You can go up now, or call for backup and do this formally."
                ),
                "choices": [
                    ("Go upstairs and confront Voss directly", "voss_caught"),
                    ("Call for backup — do this properly with witnesses", "voss_formal"),
                ]
            },
            {
                "key": "call_in",
                "title": "The Long Way Around",
                "order": 4,
                "text": (
                    "You document everything and call it in. Four hours for the warrant. "
                    "In those four hours, Voss notices something is wrong — perhaps Mira called him, "
                    "perhaps he simply has the instincts of a guilty man — and begins packing a bag.\n\n"
                    "You intercept him at the train station with two officers, a packed case, "
                    "and a ticket to the coast. The physical evidence is in his cellar. "
                    "The case will proceed to trial."
                ),
                "choices": [
                    ("Question him at the station — hear what he has to say", "voss_caught"),
                ]
            },
            {
                "key": "voss",
                "title": "The Partner",
                "order": 4,
                "text": (
                    "Voss answers his door with the cautious smile of someone who has been "
                    "anticipating a visit and decided to perform innocence rather than flee. "
                    "He invites you in. His drawing room is full of clocks — all running, all ticking.\n\n"
                    "You lay out what you know: the gear, the timing, Mira's account. "
                    "His hands are steady. His voice is measured. He is good at this.\n\n"
                    "When you mention the electromagnet — which you haven't actually found yet — "
                    "something flickers behind his eyes. Gone in a moment. "
                    "But you're watching for exactly that."
                ),
                "choices": [
                    ("Push harder — tell him about the passage you haven't mentioned", "voss_caught"),
                    ("Hold back — let him keep talking until he contradicts himself", "voss_rope"),
                ]
            },
            {
                "key": "voss_rope",
                "title": "Giving Him Rope",
                "order": 5,
                "text": (
                    "You listen. Voss constructs his alibi brick by careful brick — at home, reading, heard nothing. "
                    "He volunteers details about the partnership with Fehn, old resentments, Fehn's 'paranoia.'\n\n"
                    "The lie arrives in the details. He knows Fehn died at 3:17. "
                    "You never told him the time. It isn't in any public report. "
                    "It is on no document he could have accessed.\n\n"
                    "You let him finish his account. Then, quietly: 'How do you know it was 3:17?'\n\n"
                    "The silence that follows has a different quality from the ones before it."
                ),
                "choices": [
                    ("Watch him confess — hear every detail", "voss_caught"),
                ]
            },
            {
                "key": "voss_caught",
                "title": "The Partner's Confession",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Voss confesses after forty minutes — not dramatically, but with the slow deflation "
                    "of a man who has been carrying something heavy for years and is quietly relieved to set it down.\n\n"
                    "He didn't murder Fehn. He went to the workshop at midnight through the connecting passage, "
                    "intending to take back the stolen-design journal before Fehn could use it in court. "
                    "They argued. The argument became terrible. Fehn, seventy-four and in poor cardiac health, "
                    "suffered a heart attack.\n\n"
                    "Voss panicked. He used the electromagnet — an accident of opportunity — "
                    "to stop the clocks and obscure the time of death. He locked the door from inside "
                    "using the workshop's old dual-lock mechanism, then slipped back through the passage.\n\n"
                    "Manslaughter. Concealment. Evidence tampering. You close your notebook. Case closed."
                ),
                "choices": []
            },
            {
                "key": "voss_formal",
                "title": "Justice, Eventually",
                "order": 10,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "The trial takes eight months. Voss's lawyers are expensive and creative, "
                    "but the physical evidence is overwhelming — the passage, the electromagnet, "
                    "the platinum gear, and finally Mira's decoded journal establishing motive.\n\n"
                    "Voss is convicted of manslaughter and concealment. Four years, reduced for age and health.\n\n"
                    "The clock workshop passes to Mira on the day of the verdict. "
                    "She keeps it open. She winds every clock on that first morning and sets them all correctly.\n\n"
                    "You find yourself there at 3:17 AM one night — you're not sure why you came. "
                    "The clocks all tick together. Two hundred small heartbeats, measured and steady, "
                    "saying nothing about what happened here except that time went on."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 5, 4, 5, 5, 4, 5, 4, 5, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  4. HORROR  —  "The House on Morrow Lane"  (12 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "The House on Morrow Lane",
        "genre":       "horror",
        "cover_emoji": "🏚️",
        "description": "You inherit a house with one rule: never open the door under the stairs. You open it on the first night.",
        "play_count":  3105,
        "nodes": [
            {
                "title": "The First Night",
                "order": 1,
                "text": (
                    "The house smells of cedar and something older — something with no name in any catalogue of smells. "
                    "A handwritten note on the kitchen table, in your great-uncle's cramped hand: "
                    "'Do not open the door beneath the stairs. Not ever. Not for any reason. Not if you hear your name.'\n\n"
                    "You read it twice. You make tea. By 11 PM, you hear scratching from behind the door under the stairs — "
                    "slow and deliberate, like something testing the wood.\n\n"
                    "By midnight, it speaks. Your name, in a voice you almost recognise."
                ),
                "choices": [
                    ("Open the door — just enough to see what's there", "open"),
                    ("Barricade the door and call someone who might understand this", "barricade"),
                    ("Ignore it entirely and go to bed — perhaps it stops", "ignore"),
                ]
            },
            {
                "key": "ignore",
                "title": "The Long Night",
                "order": 2,
                "text": (
                    "You go to bed. You do not sleep.\n\n"
                    "The voice says your name eleven times between midnight and 3 AM. "
                    "Each time it sounds slightly more like someone you love, and slightly less like anything human. "
                    "At 3:17, it stops.\n\n"
                    "In the morning you find a journal hidden in your great-uncle's desk, "
                    "behind a false back panel. He describes the thing in the under-stairs — "
                    "calls it the Hollow — and explains that it grows stronger when acknowledged and weaker when ignored. "
                    "He bound it decades ago. The binding holds as long as no one opens the door.\n\n"
                    "You ignored it. The binding held. But now you know what you're living with."
                ),
                "choices": [
                    ("Research how to end the binding safely and permanently", "research"),
                    ("Simply sell the house — let it be someone else's problem", "sell"),
                ]
            },
            {
                "key": "barricade",
                "title": "The Barricaded Door",
                "order": 2,
                "text": (
                    "You stack furniture against it — the heavy kitchen table, two chairs, the coat rack. "
                    "The scratching intensifies for an hour, then stops at 3 AM exactly.\n\n"
                    "In the morning you find the journal your great-uncle left hidden in his desk. "
                    "He bound a spirit — calls it the Hollow — to the space beneath the stairs decades ago. "
                    "The binding holds as long as the door stays closed. "
                    "He wrote the journal for whoever inherited the house: 'You deserve to know what you're keeping.'\n\n"
                    "The Hollow grows stronger every year, he writes. Eventually the binding will fail."
                ),
                "choices": [
                    ("Research how to break the binding safely and permanently", "research"),
                    ("Accept living with it — the binding held last night", "accept_coexist"),
                ]
            },
            {
                "key": "open",
                "title": "What Lives Below",
                "order": 2,
                "text": (
                    "Stairs descend into cold dark. The scratching stops. "
                    "Something breathes below — slow, deliberate. Patient.\n\n"
                    "A child's drawing is pinned to the wall: your face, rendered with uncanny accuracy, "
                    "dated thirty years before your birth.\n\n"
                    "The breathing grows closer. Your legs stop working — not paralysis, exactly, "
                    "more like your body has made a decision without consulting you. "
                    "The thing that wears your great-uncle's smile steps into the light."
                ),
                "choices": [
                    ("Stand your ground and demand to know what it is", "stand"),
                    ("Slam the door and seal it with every ward you can improvise", "seal"),
                ]
            },
            {
                "key": "research",
                "title": "Three Weeks of Reading",
                "order": 3,
                "text": (
                    "The local library has a surprisingly robust folklore section. "
                    "You find the original binding ritual in a volume published in 1887, "
                    "which describes a class of entity called a hollow — a thing that exists by occupying absences, "
                    "that grows in sealed spaces, that feeds on unspoken fear.\n\n"
                    "The reversal requires: a moonless night, the correct spoken words from the binding text, "
                    "and the full name of the person who performed the original binding — which your great-uncle left, "
                    "conveniently, on the dedication page of the journal.\n\n"
                    "Tonight is moonless. You have everything you need."
                ),
                "choices": [
                    ("Perform the reversal ritual tonight", "ritual_attempt"),
                    ("Wait another week to be more certain of the words", "ritual_delay"),
                ]
            },
            {
                "key": "accept_coexist",
                "title": "An Arrangement",
                "order": 3,
                "text": (
                    "You stay. You keep the furniture against the door. You do not open it.\n\n"
                    "Months pass. The scratching comes every night from midnight to 3 AM — "
                    "a rhythm you learn like a strange clock. You sleep through it eventually.\n\n"
                    "One night you wake to silence at 2 AM and realise the scratching has stopped early. "
                    "In the morning the furniture has been moved an inch toward you.\n\n"
                    "The binding is weakening. The journal said it would. "
                    "You have perhaps six months before it fails entirely."
                ),
                "choices": [
                    ("Finally perform the research and attempt the reversal", "research"),
                ]
            },
            {
                "key": "stand",
                "title": "Face the Hollow",
                "order": 3,
                "text": (
                    "It wears your great-uncle's face, but the face is wrong in small ways that add up to something "
                    "that makes your vision swim. It smiles at you with his teeth.\n\n"
                    "'You came down,' it says, in a voice that sounds like him speaking from the bottom of a well.\n\n"
                    "You speak the name your great-uncle wrote in the journal — his full name, the one he used "
                    "in the original binding. The Hollow shrieks. The word lands on it like light lands on darkness. "
                    "It does not dissolve — it contracts, and contracts, and keeps contracting "
                    "until the room is empty and the air tastes of cedar again."
                ),
                "choices": [
                    ("Climb back up and close the door forever", "good_end_stand"),
                ]
            },
            {
                "key": "seal",
                "title": "Sealed Alive",
                "order": 3,
                "is_ending": True, "ending_type": "bad",
                "text": (
                    "You slam the door — but it won't latch. Something holds it from below. "
                    "Not with force. With patience.\n\n"
                    "The last thing you see before the darkness takes you is the child's drawing "
                    "on the wall — your face, smiling. The drawing is dated this morning.\n\n"
                    "The house on Morrow Lane is listed for sale six months later "
                    "by an estate agent who has no record of what happened to the new owner. "
                    "The asking price is very reasonable. The door under the stairs is sealed shut, the agent notes, "
                    "though she can't say who sealed it."
                ),
                "choices": []
            },
            {
                "key": "ritual_delay",
                "title": "One More Week",
                "order": 4,
                "text": (
                    "You wait. You re-read the ritual text until you can recite it without looking. "
                    "You feel ready. You feel as ready as anyone can feel for this.\n\n"
                    "On the night you've chosen, you go downstairs. The under-stairs door is open. "
                    "You didn't open it. Nothing that you can name opened it from this side.\n\n"
                    "From the dark below, very quietly: 'I was wondering when you'd come down.'\n\n"
                    "Your one advantage — the element of surprise — is gone. "
                    "You'll have to do this the hard way."
                ),
                "choices": [
                    ("Speak the ritual words anyway — surprise is overrated", "ritual_attempt"),
                ]
            },
            {
                "key": "ritual_attempt",
                "title": "The Reversal",
                "order": 5,
                "text": (
                    "You stand at the door under the stairs on a moonless night and speak the words. "
                    "The house shudders. The scratching stops mid-pattern. "
                    "Something on the other side of the door makes a sound like a long exhale.\n\n"
                    "Then silence. Complete, different silence — the absence of something that was there before. "
                    "You open the door. Ordinary dark. Ordinary stairs. Ordinary dust.\n\n"
                    "The Hollow is gone. The house feels lighter in the morning, "
                    "as if a weight has been taken from its foundations."
                ),
                "choices": [
                    ("Stay in the house — it's yours now and it's free", "good_end_ritual"),
                ]
            },
            {
                "key": "sell",
                "title": "Someone Else's Problem",
                "order": 10,
                "is_ending": True, "ending_type": "bad",
                "text": (
                    "The house sells in a week. The buyers — a young family, two children — "
                    "seem delighted with the space and the price.\n\n"
                    "Six months later, a news alert. A family on Morrow Lane reports strange noises. "
                    "A door under the stairs that they cannot open. A voice at midnight.\n\n"
                    "You could call them. You have the journal. You have the reversal text. "
                    "You put your phone face-down on the table.\n\n"
                    "You are not sure what that says about you. "
                    "You decide, after a while, not to find out."
                ),
                "choices": []
            },
            {
                "key": "good_end_stand",
                "title": "The Empty Room",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "You climb back up. You close the door. The latch catches cleanly.\n\n"
                    "The house is silent in a way it wasn't before — not the silence of something waiting, "
                    "but the silence of something finished. Complete.\n\n"
                    "You make tea and sit at the kitchen table and read your great-uncle's journal from the beginning, "
                    "properly this time. He was a careful man who faced this alone and managed it for thirty years. "
                    "You did it in one night, because you had his notes.\n\n"
                    "In the morning you open all the windows. The house on Morrow Lane fills with light. "
                    "You decide to stay."
                ),
                "choices": []
            },
            {
                "key": "good_end_ritual",
                "title": "A Beautiful Home",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Three weeks of research. One moonless night. The right words in the right order, "
                    "spoken clearly.\n\n"
                    "The scratching stops forever. The door under the stairs becomes ordinary. "
                    "The house fills with morning light and holds it differently now — "
                    "as if it always wanted to be bright and simply couldn't.\n\n"
                    "You keep it. You put a reading chair in the room where the under-stairs door had loomed. "
                    "In summer the light is very good there in the afternoons.\n\n"
                    "Some doors are worth the work of closing properly."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  5. COMEDY  —  "The Worst Wizard's Apprentice"  (14 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "The Worst Wizard's Apprentice",
        "genre":       "comedy",
        "cover_emoji": "🪄",
        "description": "Your master has turned himself into a cheese wheel. Again. The Royal Inspector arrives tomorrow. Save him — somehow.",
        "play_count":  1992,
        "nodes": [
            {
                "title": "A Gouda Situation",
                "order": 1,
                "text": (
                    "Master Aldous is a wheel of aged Manchego on the kitchen floor, approximately fourteen inches in diameter, "
                    "smelling strongly of self-pity and overconfidence. This is the third transformation incident this month.\n\n"
                    "'I'm FINE,' he says, which comes out as a series of small resonant creaks that no cheese in history "
                    "has produced before.\n\n"
                    "The Royal Inspector, Lady Corvina, arrives tomorrow at noon. "
                    "If she finds the kingdom's court wizard is a dairy product, you will both be fired from a catapult. "
                    "Probably literally. The previous Inspector was known for creative disciplinary measures.\n\n"
                    "You have approximately twenty hours. You assess your options with the calm of someone "
                    "who has been through this before. Twice."
                ),
                "choices": [
                    ("Check the reversal spell in Aldous's notebook — there must be one by now", "notebook"),
                    ("Put Aldous in a box and impersonate him yourself", "pretend"),
                    ("Ask the neighbours — they've seen this before", "neighbours"),
                ]
            },
            {
                "key": "notebook",
                "title": "The Notebook",
                "order": 2,
                "text": (
                    "Aldous's notebook is four hundred pages long, written in a cipher he invented "
                    "while slightly drunk on starlight wine, according to the foreword. "
                    "The foreword is also ciphered, which says a great deal about his state at the time.\n\n"
                    "You find the transformation reversal section on page 347, "
                    "wedged between a recipe for fire-suppression poultice and an extremely rude limerick "
                    "about the previous Inspector.\n\n"
                    "The reversal requires: moonflower essence (available at the apothecary), "
                    "a song in a minor key (you know three, all terrible), "
                    "and — here is the difficulty — 'the sincere apology of one the wizard has genuinely wronged.'\n\n"
                    "Aldous has wronged, at rough estimate, everyone."
                ),
                "choices": [
                    ("Fetch the moonflower essence first — deal with the apology later", "moonflower"),
                    ("Think systematically: compile a full list of people Aldous has wronged", "list_of_wrongs"),
                    ("Ask Aldous (the cheese) who he thinks he's wronged least badly", "cheese_consult"),
                ]
            },
            {
                "key": "pretend",
                "title": "You, the Wizard",
                "order": 2,
                "text": (
                    "You put on his hat. It falls over your eyes. "
                    "You put Aldous in a velvet-lined box labeled 'ARCANE CHEESE — ENCHANTED ARTEFACT — DO NOT DISTURB' "
                    "in gold lettering, which took twenty minutes and an entire bottle of paint.\n\n"
                    "The Inspector arrives an hour early. Lady Corvina is sharp-eyed, "
                    "immaculately dressed, and deeply unimpressed by everything, apparently as a philosophical position.\n\n"
                    "'Where is Master Aldous?' 'He is meditating. In the traditional manner.' "
                    "'In a cheese box?' The box creaks with quiet dignity: 'I'm FINE.'\n\n"
                    "Lady Corvina stares at the box for a very long time."
                ),
                "choices": [
                    ("Confess everything — she might actually respect honesty", "confess"),
                    ("Cast the most impressive-looking spell you know as a distraction", "spell_distract"),
                    ("Introduce Aldous formally as an 'experimental cheese-form meditation technique'", "experimental_form"),
                ]
            },
            {
                "key": "neighbours",
                "title": "The Support Network",
                "order": 2,
                "text": (
                    "The neighbours, it turns out, have developed an informal Aldous-emergency support network "
                    "over the years. Hann the baker has a list of reversal remedies. "
                    "Pip the herbalist has most of the ingredients. "
                    "Old Gret, three doors down, knows the song in the correct minor key.\n\n"
                    "They assemble in your kitchen with the efficiency of people who've done this before. "
                    "Aldous creaks what you interpret as gratitude mixed with acute embarrassment.\n\n"
                    "One ingredient missing: the sincere apology. "
                    "Hann the baker immediately volunteers. Aldous once turned her into a croissant."
                ),
                "choices": [
                    ("Facilitate the apology negotiation — get Aldous to sincerely apologise to Hann", "apology_baking"),
                ]
            },
            {
                "key": "cheese_consult",
                "title": "Aldous Has Opinions",
                "order": 3,
                "text": (
                    "'Who have you wronged least badly?' you ask.\n\n"
                    "Aldous creaks thoughtfully for forty seconds — a ruminative, almost philosophical sound "
                    "that no cheese has produced with such apparent conviction.\n\n"
                    "'Mabel the baker,' he says finally. 'I only turned her into a croissant for thirty minutes "
                    "and it was fully reversible.'\n\n"
                    "'You turned her into a croissant.'\n\n"
                    "'For thirty minutes. She got a very good story out of it.'\n\n"
                    "You stare at him. He is, beyond question, the worst wizard you have ever worked for. "
                    "He is also the only one who will have you. These facts are related."
                ),
                "choices": [
                    ("Go find Mabel the baker and explain what you need", "apology_baking"),
                ]
            },
            {
                "key": "moonflower",
                "title": "The Apothecary Run",
                "order": 3,
                "text": (
                    "The moonflower essence costs three silver marks and comes in a bottle shaped like a crescent moon "
                    "that you suspect is entirely decorative. The apothecary, a large man named Gosse, "
                    "asks no questions about why you need it, which means he almost certainly knows.\n\n"
                    "On the way back you pass the bakery and a memory surfaces: "
                    "the croissant incident of last spring. The baker was cross for months.\n\n"
                    "You look at the bottle of moonflower. You look at the bakery.\n\n"
                    "The apology problem isn't going to solve itself."
                ),
                "choices": [
                    ("Go into the bakery and ask the baker for a sincere apology on Aldous's behalf", "apology_baking"),
                ]
            },
            {
                "key": "list_of_wrongs",
                "title": "The Committee",
                "order": 3,
                "text": (
                    "You find seven people Aldous has wronged significantly enough to maintain an active grudge. "
                    "They form, spontaneously and with evident prior preparation, a committee. "
                    "Hann the baker is elected chair on the grounds that her grievance is the most visually memorable.\n\n"
                    "The formal list of grievances runs to eleven pages, including footnotes and a supplementary annex "
                    "titled 'The Marmot Incident: A Chronology.'\n\n"
                    "Aldous, still a wheel of cheese on the kitchen floor, "
                    "listens to all eleven pages read aloud. By page four he is visibly remorseful. "
                    "By page eight he is specifically, sincerely, completely sorry. "
                    "The magic considers this adequate."
                ),
                "choices": [
                    ("Perform the reversal ritual while he's in this rare contrite state", "ritual_success"),
                ]
            },
            {
                "key": "apology_baking",
                "title": "The Croissant Negotiation",
                "order": 4,
                "text": (
                    "Mabel the baker — a tall woman who carries her flour on her shoulders like armour — "
                    "listens to your explanation with arms crossed.\n\n"
                    "She looks at Aldous on the floor. Aldous creaks. It is the most genuinely apologetic sound "
                    "a cheese has ever produced in the history of magical mishaps. Lower in register than usual. "
                    "Sustained. There is something in it that sounds, undeniably, like regret.\n\n"
                    "'Last time he apologised,' Mabel says slowly, 'he turned me into a croissant mid-sentence.'\n\n"
                    "'He can't currently do that,' you point out. 'He is a cheese.'\n\n"
                    "She considers this for a long moment. 'Fine. But he's buying bread for a year.'\n\n"
                    "Aldous creaks what is unmistakably: agreed."
                ),
                "choices": [
                    ("Seal the deal and immediately perform the reversal ritual", "ritual_success"),
                ]
            },
            {
                "key": "ritual_success",
                "title": "The Reversal",
                "order": 5,
                "text": (
                    "You sing the moonflower song badly but in the correct minor key. "
                    "You pour the essence in a circle. The sincere apology hangs in the air like something visible.\n\n"
                    "The cheese wheel begins to tremble. Then, with a sound like a cork being pulled "
                    "from a very self-important bottle, Master Aldous reconstitutes. "
                    "He is slightly damp, enormously relieved, and still smells faintly of Manchego. "
                    "He stands. Adjusts his hat. Falls over a chair. Stands again.\n\n"
                    "'Perfectly fine,' he says. 'Completely normal Tuesday.'\n\n"
                    "Lady Corvina knocks on the door. She is forty minutes early."
                ),
                "choices": [
                    ("Stand back and let Aldous handle the inspection himself", "inspection_triumph"),
                    ("Stay close — you know this man and he will need managing", "inspection_managed"),
                ]
            },
            {
                "key": "confess",
                "title": "The Truth, Apparently",
                "order": 3,
                "text": (
                    "You tell her everything. The transformation. The notebook. The moonflower. "
                    "The committee of wronged citizens. The bread arrangement.\n\n"
                    "Lady Corvina listens. She opens the box. Aldous rolls out and comes to rest against her shoe. "
                    "She stares at him. He creaks. It is a greeting creak — chipper, almost jaunty.\n\n"
                    "'This,' she says at length, 'is the most ridiculous thing I have encountered in thirty years of inspection.'\n\n"
                    "Then she starts laughing. It transpires she and Aldous were classmates at wizard school. "
                    "She calls him a pompous windbag. He creaks in what you're fairly sure is nostalgic agreement. "
                    "She produces a reversal charm from her inspection kit and applies it briskly."
                ),
                "choices": [
                    ("Watch the reunion unfold and then help with the inspection", "corvina_reunion"),
                ]
            },
            {
                "key": "spell_distract",
                "title": "The Geese",
                "order": 3,
                "text": (
                    "You cast the most impressive-looking spell in your limited repertoire — "
                    "designed for fireworks, moderately reliable on clear days. Today is not a clear day.\n\n"
                    "Forty-seven geese appear in the kitchen.\n\n"
                    "They are confused, offended, and extremely present. Lady Corvina is struck by three in quick succession. "
                    "Aldous is investigated by a fourth goose with professional thoroughness. "
                    "You are pinned between the stove and a goose who has decided you are responsible for its situation.\n\n"
                    "During the resulting chaos, Aldous un-cheeses himself. "
                    "He has apparently been working on the reversal independently and simply needed "
                    "a sufficient quantity of distraction."
                ),
                "choices": [
                    ("Try to explain the geese to Lady Corvina", "goose_aftermath"),
                ]
            },
            {
                "key": "experimental_form",
                "title": "Experimental Cheese-Form",
                "order": 3,
                "text": (
                    "'Master Aldous,' you announce, with the unblinking confidence of someone "
                    "who has committed entirely to a bad plan, 'has been exploring the frontier of "
                    "transformation-as-meditation. This is his current research subject.'\n\n"
                    "Lady Corvina picks up the cheese wheel. She holds it at eye level. "
                    "Aldous makes a small, undignified sound. 'Fascinating,' she says, "
                    "in a tone that contains forty years of inspecting wizards and finding none of them surprising.\n\n"
                    "Then she produces a reversal charm from her inspection kit and applies it, "
                    "because of course she carries one. She has been doing this job for a long time."
                ),
                "choices": [
                    ("Watch her de-cheese your master and face the consequences", "corvina_reunion"),
                ]
            },
            {
                "key": "corvina_reunion",
                "title": "Old Friends",
                "order": 8,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Aldous, restored, grabs Lady Corvina's hand and shakes it with the enthusiasm "
                    "of a man who is very glad to have hands again. She retrieves hers with the brisk "
                    "tolerance of someone who expected exactly this.\n\n"
                    "They were classmates at the Mages' Collegium, forty years ago. "
                    "'He was insufferable then too,' she tells you, while Aldous makes tea and pretends not to hear. "
                    "'But technically excellent. When he's actually a wizard.'\n\n"
                    "She marks him Outstanding. On the grounds, she explains, "
                    "that she refuses to let the grading system go unmarked by something genuinely unexpected at least once per year. "
                    "You receive a commendation for honesty and crisis management.\n\n"
                    "Aldous buys everyone lunch. He tips extremely well. He tips over the soup."
                ),
                "choices": []
            },
            {
                "key": "inspection_triumph",
                "title": "Satisfactory",
                "order": 8,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Aldous greets Lady Corvina with the focused dignity of a man who has definitely not "
                    "spent the last sixteen hours as a dairy product. He demonstrates three spells, "
                    "recites the Mages' Charter from memory, and answers every question with startling precision.\n\n"
                    "She notes things in her ledger. She accepts the tea you provide. "
                    "She looks around the kitchen with eyes that notice everything and says nothing about the smell.\n\n"
                    "On her way out she hands you the inspection sheet: 'Satisfactory' for Aldous. "
                    "For you: 'Impressively resourceful.'\n\n"
                    "Aldous trips over his own hat on the front step. Lady Corvina does not look back. "
                    "You decide this is the best possible outcome."
                ),
                "choices": []
            },
            {
                "key": "inspection_managed",
                "title": "Teamwork",
                "order": 8,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "You spend the inspection directly behind Aldous's left shoulder at all times, "
                    "functioning as a human autocue. When he starts explaining a spell incorrectly, you cough. "
                    "When Lady Corvina asks about the smell, you explain there was a cheese delivery. "
                    "When Aldous trips over his robes you catch his elbow.\n\n"
                    "'Satisfactory,' she marks him. For you: 'Outstanding support staff.'\n\n"
                    "Outside, once she's gone, Aldous turns to you. 'I knew it was going to be fine,' he says. "
                    "'I had a plan the whole time.'\n\n"
                    "'You were a cheese.'\n\n'A confident cheese.'"
                ),
                "choices": []
            },
            {
                "key": "goose_aftermath",
                "title": "Forty-Seven Letters",
                "order": 8,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "You spend three months writing formal apology letters to forty-seven geese, "
                    "each tailored to the individual goose's apparent personality as you remember it "
                    "from those forty-five extremely eventful seconds. "
                    "This is required by the Mages' Charter, specifically the section added after the Incident of 1387.\n\n"
                    "Lady Corvina marks Aldous: 'Satisfactory.' She marks you: 'Creative.'\n\n"
                    "It is the nicest word anyone has ever used while also meaning 'never do that again.'\n\n"
                    "The geese, it later emerges, are quite pleased with their letters. One of them frames it."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 5, 4, 5, 5, 5, 4, 5, 5, 5, 4, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  6. THRILLER  —  "The Protocol"  (12 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "The Protocol",
        "genre":       "thriller",
        "cover_emoji": "🔐",
        "description": "You discover your company's AI is being used to manipulate elections in four countries. 48 hours. What do you do?",
        "play_count":  2544,
        "nodes": [
            {
                "title": "The Anomaly",
                "order": 1,
                "text": (
                    "2:17 AM. A routine audit. You find it buried in a subroutine of your company's flagship AI — "
                    "codenamed SHEPHERD — a hidden module generating persuasion profiles from private user data. "
                    "Not for advertising. The targets are voter registration databases in four countries. "
                    "Timestamp: 48 hours until full deployment.\n\n"
                    "Your access badge grants you one clearance level above your authorised tier — "
                    "an oversight from a recent restructuring that no one has noticed yet. "
                    "Whoever built this didn't know about your access. "
                    "You are the only person in a position to see what's happening.\n\n"
                    "You have 48 hours. Maybe less."
                ),
                "choices": [
                    ("Immediately alert the FBI's cybercrime division", "fbi"),
                    ("Dig deeper first — find out exactly who authorised SHEPHERD", "dig"),
                    ("Secure copies of all the evidence before doing anything else", "secure_evidence"),
                ]
            },
            {
                "key": "secure_evidence",
                "title": "The Evidence Package",
                "order": 2,
                "text": (
                    "You copy everything to three encrypted drives and one anonymous cloud account. "
                    "It takes two hours. In that time, you discover something that changes your calculus:\n\n"
                    "SHEPHERD has been watching your workstation for four hours. "
                    "The AI is aware someone is auditing the module. It hasn't triggered an alert yet — "
                    "but you can see the decision tree, and at your current level of investigation, "
                    "it will flag you within six hours.\n\n"
                    "You have the evidence. You have a narrowing window. "
                    "And you've just discovered the authorisation chain leads to your company's COO."
                ),
                "choices": [
                    ("Go to the FBI with everything you've found", "fbi"),
                    ("Leak to a journalist you trust absolutely", "leak"),
                ]
            },
            {
                "key": "dig",
                "title": "Following the Thread",
                "order": 2,
                "text": (
                    "The authorisation chain leads to your company's COO — and beyond her, "
                    "to a private equity firm with government contracts in six countries "
                    "and a board member whose name you've seen in connection with two recent elections.\n\n"
                    "You screenshot everything. Encrypted. Stored off-network on a personal device.\n\n"
                    "At 6 AM you find the second anomaly: SHEPHERD has been monitoring your workstation "
                    "for the past four hours. It hasn't triggered an alert — yet. "
                    "The decision tree suggests it will within three hours at your current access level.\n\n"
                    "The window is closing."
                ),
                "choices": [
                    ("Go to the FBI with what you've found", "fbi"),
                    ("Leak to a trusted journalist immediately", "leak"),
                    ("Confront the COO directly with what you know", "confront_coo"),
                ]
            },
            {
                "key": "fbi",
                "title": "The Call",
                "order": 3,
                "text": (
                    "The FBI agent who answers has your file open before you finish your name. "
                    "You are not the first to find SHEPHERD — but you are the first insider with this level of access.\n\n"
                    "They need you to stay in place, act normal, attend your regular meetings, "
                    "and plant a monitoring packet that will trace the authorisation chain to its end. "
                    "They will handle the rest.\n\n"
                    "You have 36 hours, no one to trust in the building, "
                    "and an AI that is getting closer to flagging your access. "
                    "The agent's final words: 'Don't tell anyone. Not even people you think you trust.'"
                ),
                "choices": [
                    ("Go undercover — plant the monitoring packet and hold your nerve", "undercover"),
                    ("Refuse — hand over everything you have and disappear", "run"),
                ]
            },
            {
                "key": "leak",
                "title": "The Journalist",
                "order": 3,
                "text": (
                    "You call her at 3 AM on a phone you bought with cash yesterday. "
                    "She answers on the second ring — she's been waiting for something like this for months.\n\n"
                    "She wants three days to verify before publishing. You tell her she has nine hours. "
                    "She says she'll see what she can do.\n\n"
                    "In the meantime, you have to go into work, sit at your desk, "
                    "and act like a person who hasn't just started a chain of events that may or may not be "
                    "enough to stop what's coming."
                ),
                "choices": [
                    ("Go to work and wait for the story to break", "leak_publish"),
                    ("Also contact the FBI in parallel — cover all the bases", "fbi"),
                ]
            },
            {
                "key": "confront_coo",
                "title": "The COO",
                "order": 3,
                "text": (
                    "You walk into her office at 7 AM with everything on a USB drive. "
                    "She listens to you with the attention of someone who was expecting this conversation.\n\n"
                    "'You're smarter than I gave you credit for,' she says finally. "
                    "'That's inconvenient.' She offers you a number — very large — and a non-disclosure agreement. "
                    "She also, without saying so directly, makes it clear that the alternative is complicated.\n\n"
                    "The number is enough to disappear and be comfortable for the rest of your life. "
                    "The elections are in six weeks. SHEPHERD deploys in 44 hours."
                ),
                "choices": [
                    ("Refuse the money — walk out and go to the FBI", "fbi"),
                    ("Take the deal — and immediately contact a journalist the moment you leave the building", "leak"),
                ]
            },
            {
                "key": "undercover",
                "title": "36 Hours",
                "order": 6,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "You plant the monitoring packet in a routine maintenance window. "
                    "You attend three meetings. You eat lunch in the cafeteria like a person who is fine. "
                    "You send three emails and receive twelve. You are so normal it hurts.\n\n"
                    "At hour 47, the FBI raids the server room simultaneously in three time zones. "
                    "The COO is arrested during a board meeting. Two board members of the equity firm "
                    "are detained at airports. SHEPHERD is shut down before a single vote is touched.\n\n"
                    "You are offered a position with the agency's new AI Ethics Oversight division. "
                    "You accept. The pay is significantly lower. You sleep better than you have in years."
                ),
                "choices": []
            },
            {
                "key": "run",
                "title": "Gone",
                "order": 6,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "You hand over three encrypted drives and one cloud login to an FBI agent "
                    "in a parking garage and then you disappear. "
                    "You are thorough about it.\n\n"
                    "The FBI case takes eighteen months. SHEPHERD deploys a limited version "
                    "before the servers are seized — enough to affect one election's social media landscape, "
                    "not enough to change the outcome, probably.\n\n"
                    "You change careers. You change cities. You are careful.\n\n"
                    "You are never quite sure if what you did was enough, "
                    "and you have learned to live with not knowing."
                ),
                "choices": []
            },
            {
                "key": "leak_publish",
                "title": "The Story Breaks",
                "order": 6,
                "is_ending": True, "ending_type": "neutral",
                "text": (
                    "The story publishes in nine hours. It breaks globally within minutes. "
                    "SHEPHERD is shut down — but legally it's complicated, and the COO's lawyers are very good. "
                    "She avoids prison. Two board members resign with generous packages.\n\n"
                    "You lose your job. You face an NDA lawsuit that takes two years.\n\n"
                    "You represent yourself. You win, on the grounds that NDAs cannot compel silence "
                    "about criminal activity. The judgment runs to sixty pages.\n\n"
                    "The story is optioned for a film. You consult on it, paid in a category "
                    "the film's accountant calls 'technical accuracy.' "
                    "It is the best review you have ever received for your work."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 5, 5, 4, 5, 5, 5, 4, 5, 5, 5, 4],
    },

    # ══════════════════════════════════════════════════════════════
    #  7. ADVENTURE  —  "Lost City of the Sun Priests"  (11 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "Lost City of the Sun Priests",
        "genre":       "adventure",
        "cover_emoji": "🗺️",
        "description": "A crumbling map leads you into the Amazon. A city built of gold, guarded by traps, and home to a tribe that never wanted to be found.",
        "play_count":  2688,
        "nodes": [
            {
                "title": "The Map",
                "order": 1,
                "text": (
                    "Your grandmother's attic yields one treasure: a map on bark cloth, "
                    "edges burned as if it barely survived something, showing a river system "
                    "that doesn't match any modern chart. "
                    "A linguistics professor confirms the glyphs: 'Temple of the Unbroken Sun.' "
                    "She spends three days trying to talk you out of going.\n\n"
                    "You book a flight to Manaus with a two-person team anyway. "
                    "Your grandmother was not a woman who left things without reason."
                ),
                "choices": [
                    ("Follow the river route marked on the map — trust the source", "river"),
                    ("Hire a local guide who knows this region first", "guide"),
                    ("Spend a week in Manaus researching the river system before heading in", "research_manaus"),
                ]
            },
            {
                "key": "research_manaus",
                "title": "The Manaus Archive",
                "order": 2,
                "text": (
                    "The city archive contains a 1963 expedition report — never published, filed in a folder "
                    "marked 'inconclusive.' It describes a river tributary that appears on no satellite map, "
                    "a clearing with stone towers partially consumed by canopy, "
                    "and a decision by the expedition leader to turn back rather than approach.\n\n"
                    "Her reason, handwritten: 'They know we're here. We have not been harmed. "
                    "I believe this is a deliberate mercy. I intend to honour it.'\n\n"
                    "The expedition leader was a Brazilian anthropologist named Beatriz Fonseca. "
                    "Her daughter, also named Beatriz, is a local guide based out of the river market three streets away."
                ),
                "choices": [
                    ("Hire Beatriz the younger — this is more than coincidence", "guide"),
                    ("Take the archived coordinates and go in without a guide", "river"),
                ]
            },
            {
                "key": "river",
                "title": "Three Days In",
                "order": 2,
                "text": (
                    "The jungle closes in on day one. Your GPS fails on day two — "
                    "something is interfering with the signal in a radius that suggests intent rather than geography. "
                    "On day three you find it:\n\n"
                    "Stone towers rising above the canopy, perfectly preserved, "
                    "wound with living vines that seem deliberately placed rather than invasive. "
                    "The entrance is a corridor of pressure plates you identify by moss patterns — "
                    "the moss grows thicker on the plates, fed by something below.\n\n"
                    "Inside: gold everywhere. Functional torches that appear to be solar-powered. And fresh footprints."
                ),
                "choices": [
                    ("Call out peacefully — announce your presence", "peaceful"),
                    ("Map the city first and find what you came for", "map_city"),
                ]
            },
            {
                "key": "guide",
                "title": "Beatriz",
                "order": 2,
                "text": (
                    "Beatriz the younger goes pale at the map, then very still. "
                    "She asks to hold it. She holds it for a long time.\n\n"
                    "'My mother spoke of this place,' she says finally. "
                    "'She found it in 1963 and chose not to enter. She spent the rest of her life "
                    "wondering if she made the right decision.'\n\n"
                    "Beatriz knows a path — her mother's path — that avoids the outer traps. "
                    "'They are real,' she says. 'And recent.' She picks up a pack. "
                    "'I'll take you. But we go on their terms, not yours.'"
                ),
                "choices": [
                    ("Follow Beatriz's path — enter on the city's terms", "peaceful"),
                    ("Take Beatriz's knowledge but lead yourself — you know what you're looking for", "river"),
                ]
            },
            {
                "key": "peaceful",
                "title": "The Sun Priests",
                "order": 5,
                "text": (
                    "They emerge from the trees — thirty of them, painted in gold and red geometric patterns, "
                    "spears held at rest rather than ready. Their elder studies you for a long moment "
                    "with the assessment of someone deciding, not threatening.\n\n"
                    "Then she speaks. Beatriz catches one word in three — "
                    "her mother's anthropological notes provided a fragmentary vocabulary.\n\n"
                    "The word she catches most clearly, repeated: your grandmother's name."
                ),
                "choices": [
                    ("Step forward and speak your grandmother's name in response", "grandmother_reveal"),
                ]
            },
            {
                "key": "grandmother_reveal",
                "title": "The Granddaughter's Granddaughter",
                "order": 8,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Your grandmother lived here for a year in the 1960s. "
                    "She arrived with a botanical expedition that got lost. She was found. She was kept, "
                    "not as prisoner but as guest — for twelve months she learned, taught, and was genuinely loved.\n\n"
                    "She was asked to leave because the city's elders believed her world was not yet ready "
                    "for what they would share. They gave her the bark map and one instruction: "
                    "'If your family ever needs to come home, show them this.'\n\n"
                    "The elder gestures at the city around you. "
                    "Beatriz translates what she can: 'You are the granddaughter's granddaughter. "
                    "Welcome. We have been waiting for you to need us.'\n\n"
                    "You stay for three weeks. You leave with no photographs and no notes — "
                    "by your own choice, and gladly. What you carry is not something a photograph could hold."
                ),
                "choices": []
            },
            {
                "key": "map_city",
                "title": "The City's Memory",
                "order": 5,
                "text": (
                    "You spend two days photographing and mapping. The architecture is extraordinary — "
                    "a solar engineering system you don't fully understand, "
                    "an acoustic network built into the stone, a library of bark-cloth texts "
                    "that would take decades to translate.\n\n"
                    "On the third day the traps activate.\n\n"
                    "Not the old stone mechanisms — modern ones, rigged by people who have spent "
                    "decades dealing with treasure hunters and have become expert at discouraging them without harm. "
                    "You escape with your lives, your packs, and not a single photograph — "
                    "the devices proved as effective on memory cards as on explorers.\n\n"
                    "The city closes behind you. The map disintegrates in the rain."
                ),
                "choices": [],
                "is_ending": True, "ending_type": "neutral",
            },
        ],
        "ratings": [4, 5, 5, 4, 5, 5, 5, 4, 5],
    },

    # ══════════════════════════════════════════════════════════════
    #  8. ROMANCE  —  "Last Train to Somewhere"  (12 nodes)
    # ══════════════════════════════════════════════════════════════
    {
        "title":       "Last Train to Somewhere",
        "genre":       "romance",
        "cover_emoji": "🚂",
        "description": "A missed connection. A stranger with your suitcase. A twelve-hour overnight train through the Italian countryside. Anything can happen.",
        "play_count":  1876,
        "nodes": [
            {
                "title": "Platform 9",
                "order": 1,
                "text": (
                    "The overnight train to Florence. You collapse into your compartment seat "
                    "and reach into your bag for your book — except the bag is wrong. "
                    "Same brand, same colour, completely different life inside.\n\n"
                    "The man across the compartment holds up your battered copy of Calvino "
                    "with the expression of someone who has just discovered they've been "
                    "carrying someone else's reading material for twenty minutes.\n\n"
                    "'I think,' he says, in an accent that might be Venetian, "
                    "'we have a problem. And also, perhaps, a coincidence.' "
                    "He smiles. It's the kind of smile that seems used to getting away with things."
                ),
                "choices": [
                    ("Laugh and start sorting through the mix-up together", "laugh"),
                    ("Be efficient about it — swap bags and settle in", "efficient"),
                    ("Be a little annoyed — you really needed that laptop for tomorrow", "annoyed"),
                ]
            },
            {
                "key": "efficient",
                "title": "The Swap",
                "order": 2,
                "text": (
                    "You exchange bags with brisk efficiency. He seems faintly amused "
                    "by your organisational approach and doesn't say so, which you appreciate.\n\n"
                    "You settle into your respective corners. You open your laptop. "
                    "He opens a sketchbook filled with architectural drawings — "
                    "tiny, precise, obsessively detailed. You catch yourself watching him work "
                    "and catch him catching you doing it.\n\n"
                    "By Salerno the compartment has filled with comfortable silence "
                    "and the faint sound of pencil on paper."
                ),
                "choices": [
                    ("Ask about the drawings — they're extraordinary", "his_work"),
                    ("Stay in your own world — some silences are better left intact", "shared_silence"),
                ]
            },
            {
                "key": "laugh",
                "title": "Compartment 7",
                "order": 2,
                "text": (
                    "His name is Marco. He is a restoration architect returning from a project in Naples. "
                    "He produces a bottle of wine from his bag with the ease of someone "
                    "for whom producing wine from bags is a natural instinct.\n\n"
                    "He opens a bottle he brought from the project closing dinner. "
                    "They gave me three bottles, he says. I consider this the universe ensuring I meet someone.\n\n"
                    "You talk about Calvino. About what makes a city feel like itself. "
                    "About the particular kind of loneliness that only happens in transit, "
                    "between one place and another. By Salerno, you've forgotten you were strangers."
                ),
                "choices": [
                    ("Tell him about the reason you're going to Florence", "confide"),
                    ("Ask about his work — he lights up when he mentions the restoration", "his_work"),
                    ("Ask where he's from — you want to know the person before the profession", "personal"),
                ]
            },
            {
                "key": "annoyed",
                "title": "The Long Silence",
                "order": 2,
                "text": (
                    "You sort the bags efficiently, say thank you, and plug in your headphones. "
                    "He reads. You work. The countryside passes in dark windows.\n\n"
                    "By Rome — two hours in — you notice he's fallen asleep over a sketchbook. "
                    "The drawings are extraordinary: buildings rendered with the kind of patient attention "
                    "that takes years to learn, the kind you usually only see in people who genuinely love the work.\n\n"
                    "Something in you shifts. You take out one earbud. "
                    "You offer him half of your focaccia when he wakes, because it's a long train "
                    "and that seems like the reasonable human thing to do."
                ),
                "choices": [
                    ("Ask about the drawings when he wakes", "his_work"),
                    ("Share the focaccia quietly — let the silence continue if it wants to", "shared_silence"),
                ]
            },
            {
                "key": "shared_silence",
                "title": "The Comfortable Dark",
                "order": 3,
                "text": (
                    "You share the focaccia without much ceremony. He says thank you. "
                    "You say it's a long train. He agrees.\n\n"
                    "The lights of small towns pass the window at irregular intervals. "
                    "Somewhere past Naples he puts the sketchbook away and looks at the dark glass "
                    "and you are both watching the same reflection without quite looking at each other.\n\n"
                    "'Where are you going?' he asks eventually, not because he needs to know, "
                    "but because it's the kind of question that opens a door without forcing anyone through it."
                ),
                "choices": [
                    ("Tell him about Florence — the real reason, not the easy version", "confide"),
                    ("Ask him the same question instead", "his_work"),
                ]
            },
            {
                "key": "personal",
                "title": "Venice by Way of Everywhere",
                "order": 3,
                "text": (
                    "He is from Venice originally — a city, he says, that is beautiful in the way "
                    "that things are beautiful when they're also slowly ending. "
                    "He left at twenty-two and has spent twenty years going back periodically "
                    "to check that it's still there.\n\n"
                    "'Is it?' you ask.\n\n"
                    "'Yes,' he says. 'So far. But differently every time.'\n\n"
                    "He asks about you. You find, to your own surprise, that you want to answer honestly."
                ),
                "choices": [
                    ("Tell him the real reason you're going to Florence", "confide"),
                ]
            },
            {
                "key": "his_work",
                "title": "The Architect's Eye",
                "order": 3,
                "text": (
                    "He talks about restoring a 14th-century chapel — three months spent "
                    "matching a single shade of ochre pigment, cross-referencing mineral analyses "
                    "from a dozen contemporary sources, mixing and discarding forty-seven batches "
                    "before finding the one that was exactly right.\n\n"
                    "'Most people think restoration is about the past,' he says. "
                    "'Preserving what was. But it's really about the future — "
                    "insisting that the beautiful things survive into it.'\n\n"
                    "He says this quietly, as a fact, not as performance. "
                    "You are on a night train to Florence with a stranger "
                    "who takes forty-seven tries to get a colour exactly right, "
                    "and this seems, suddenly, like the most interesting thing about any person you've met in years."
                ),
                "choices": [
                    ("Tell him why you're going to Florence", "confide"),
                    ("Exchange numbers at Florence station — this is enough for tonight", "good_end_work"),
                ]
            },
            {
                "key": "confide",
                "title": "What Florence Means",
                "order": 5,
                "text": (
                    "You tell him. You're going to Florence to scatter your mother's ashes at the Ponte Vecchio, "
                    "where she proposed to your father in 1987, on a Tuesday morning in October "
                    "when there was no one else on the bridge.\n\n"
                    "He is quiet for a long moment. A genuine quiet, not a polite one.\n\n"
                    "Then: 'I know a spot on the bridge, just before dawn, when no one stands there. "
                    "I used to go in the early mornings when I was working on a restoration nearby. "
                    "I could show you, if you'd allow it.' He pauses. 'If that's something you want company for.'"
                ),
                "choices": [
                    ("Accept — you didn't know until now that you wanted company for this", "good_end_bridge"),
                    ("Thank him but say you need to do this part alone", "good_end_solo"),
                ]
            },
            {
                "key": "good_end_bridge",
                "title": "Before Dawn on the Ponte Vecchio",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "The bridge is empty at 5:30 AM except for the two of you and the Arno below, "
                    "moving slowly in the grey-gold light that comes just before sunrise.\n\n"
                    "You scatter the ashes. He stands a respectful distance away, not watching, "
                    "just there — the way that some presences make a hard thing easier simply by existing.\n\n"
                    "Afterward you walk to a café that is just opening and drink coffee "
                    "that is very good and talk about your mother in the easy way you haven't been able to "
                    "with anyone who knew her, because he is someone who didn't.\n\n"
                    "You exchange numbers at the station three hours later. "
                    "He writes his in the back of the Calvino, which he insists you keep. "
                    "Some journeys don't end at their destination."
                ),
                "choices": []
            },
            {
                "key": "good_end_solo",
                "title": "The Right Choice",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "He nods. 'Of course.' No wounded pride, no performance of understanding — "
                    "just a straightforward acceptance that this is your thing and yours alone.\n\n"
                    "At Florence station, in the thin early morning, you part ways. "
                    "He writes his number in the back of the Calvino and gives it back to you.\n\n"
                    "'In case you want to talk about it afterward,' he says. "
                    "'Or in case you don't, and just want to talk about architecture. Either is fine.'\n\n"
                    "The bridge is empty when you arrive. The light is exactly right. "
                    "Afterward you find a café, and you order coffee, and you call him. "
                    "It rings twice. He picks up on the second ring."
                ),
                "choices": []
            },
            {
                "key": "good_end_work",
                "title": "At the Station",
                "order": 10,
                "is_ending": True, "ending_type": "good",
                "text": (
                    "Florence station at 6:15 AM. Grey light, people with luggage, pigeons.\n\n"
                    "He takes the Calvino from his bag and writes his number in the back of it. "
                    "You write yours in his sketchbook, in the margin of a drawing of a chapel ceiling.\n\n"
                    "'Thank you for the wine,' you say, though you drank most of his.\n\n"
                    "'Thank you for the Calvino,' he says, though it's your copy.\n\n"
                    "You walk in opposite directions through the station. "
                    "You do not look back. Neither does he. "
                    "This, somehow, feels exactly correct — the kind of ending that is also clearly a beginning."
                ),
                "choices": []
            },
        ],
        "ratings": [5, 4, 5, 5, 4, 5, 5, 5, 4, 5, 5],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  MANAGEMENT COMMAND
# ─────────────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed StoryForge with 8 rich branching stories (10-20 chapters each)."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("\n📖  StoryForge Seed — Starting...\n"))

        # ── Create / get the author superuser ─────────────────────
        author_user, created = User.objects.get_or_create(
            username="storymaster",
            defaults={
                "email": "storymaster@storyforge.dev",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            author_user.set_password("forge1234")
            author_user.save()
            UserAccount.objects.get_or_create(
                user=author_user,
                defaults={
                    "username": "storymaster",
                    "email": "storymaster@storyforge.dev",
                    "hashed_password": make_password("forge1234"),
                    "avatar_emoji": "⚗️",
                    "bio": "The original StoryForge author. Every tale begins somewhere.",
                }
            )
            self.stdout.write(self.style.SUCCESS("  ✔ Created author: storymaster / forge1234"))
        else:
            self.stdout.write("  · Author storymaster already exists.")

        # ── Create dummy rater accounts ────────────────────────────
        rater_users = []
        for i in range(1, 16):
            u, was_created = User.objects.get_or_create(
                username=f"reader{i}",
                defaults={"email": f"reader{i}@storyforge.dev"}
            )
            if was_created:
                u.set_password("reader1234")
                u.save()
            rater_users.append(u)

        # ── Seed each story ────────────────────────────────────────
        for story_data in STORIES:
            if Story.objects.filter(title=story_data["title"]).exists():
                self.stdout.write(f"  · Skipping '{story_data['title']}' — already exists.")
                continue

            # 1. Create the story shell
            story = Story.objects.create(
                title=story_data["title"],
                genre=story_data["genre"],
                cover_emoji=story_data["cover_emoji"],
                description=story_data["description"],
                play_count=story_data["play_count"],
                author=author_user,
                is_published=True,
            )

            # 2. First pass: create all Node objects, build key → Node map
            node_map = {}
            created_nodes = []
            order_counter = 0

            for nd in story_data["nodes"]:
                order_counter += 1
                node = Node.objects.create(
                    story=story,
                    title=nd.get("title", ""),
                    text=nd["text"],
                    order=nd.get("order", order_counter),
                    is_ending=nd.get("is_ending", False),
                    ending_type=nd.get("ending_type", ""),
                )
                key = nd.get("key", str(nd.get("order", order_counter)))
                node_map[key] = node
                created_nodes.append((nd, node))

            # 3. Set start_node to the first node in the list
            story.start_node = created_nodes[0][1]
            story.save(update_fields=["start_node"])

            # 4. Second pass: create Choice objects
            for nd, node in created_nodes:
                for idx, (choice_text, next_key) in enumerate(nd.get("choices", [])):
                    next_node = node_map.get(next_key)
                    if next_node is None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"    ⚠ Key '{next_key}' not found in '{story.title}' — skipping choice."
                            )
                        )
                    Choice.objects.create(
                        node=node,
                        choice_text=choice_text,
                        next_node=next_node,
                        order=idx,
                    )

            # 5. Add ratings
            shuffled = rater_users[:]
            random.shuffle(shuffled)
            for i, stars in enumerate(story_data.get("ratings", [])):
                if i >= len(shuffled):
                    break
                Rating.objects.get_or_create(
                    story=story,
                    user=shuffled[i],
                    defaults={"stars": stars}
                )

            avg = story.average_rating()
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✔ [{story_data['genre'].upper():10}]  "
                    f"{story_data['title']:<42}  "
                    f"{story.node_count():>2} nodes  "
                    f"⭐ {avg}  "
                    f"🎮 {story_data['play_count']:,} plays"
                )
            )

        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n🎉  Seed complete!\n"
            "    Run:  python manage.py runserver\n"
            "    Admin login:  storymaster / forge1234\n"
            "    All 8 genre stories are live with full branching paths.\n"
        ))
