This is a genuinely ambitious project with some real architectural challenges — but the good news is that the dependencies are fairly clear once you map them out. Let me help you think through this strategically.

## The Core Problem You're Facing

You're essentially building three systems that need to work together:

1. **The simulation engine** (network, computers, filesystems, execution)
2. **The user interface** (curses-based terminal simulation)
3. **The game layer** (progression, objectives, story)

The mistake people make is trying to build all three at once. You need to reverse that order and build from the foundation up, but *prototype the top layer early* so you know the simulation is actually fun.

---

## A Phased Development Approach

### Phase 0: Architectural Prototyping (1–2 weeks)

Before you write much production code, you need to answer some hard questions about your core systems:

**The Filesystem/Program Model**
- How do you represent a "program"? Is it bytecode? AST? Just a string that gets interpreted line-by-line?
- When a program runs, what's the execution context? (Does it have stdin/stdout? Environment variables? Working directory?)
- How does memory actually work? Is it per-process, per-user, or per-computer?
- Can multiple programs run simultaneously on one computer, or is it single-threaded?

**The Access Control Model**
- Users have credentials (username/password) and access levels. Do files have owners and permissions like Unix? (rwx for user/group/other?)
- If I'm a low-privilege user and I compromise a system, how do I escalate to admin? Does compromising = RCE as that user?
- Can I run a program *as a different user*? (sudo-like behavior?)

**The Network Topology**
- Trees are simple, but can nodes be in multiple trees or have multiple parents? (If you want to model a more complex network later, this matters.)
- How do connections work? Can I only reach adjacent nodes, or can I route through intermediate nodes?

**Prototype this in pseudocode or a minimal script first.** Write out what `run_program(computer, program, user)` actually does step-by-step. This will expose gaps immediately.

---

### Phase 1: Foundation—The Simulation Engine (3–4 weeks)

Build the non-visual simulation first. You want a testable, deterministic game engine that has *nothing* to do with curses yet.

**Start with:**
1. **Computer/Node class** — just the data structure
   - Filesystem (nested dict or actual tree of File objects)
   - User accounts (username → User object with credentials, groups, permissions)
   - Running processes (list of active Program instances)
   - Network adjacency

2. **Filesystem abstraction**
   - File class (path, owner, permissions, content)
   - Directory class (acts like a File but holds children)
   - Path resolution (handle `..`, `.`, absolute vs relative)
   - This is small but must be bulletproof — it's the foundation

3. **Program/Binary model**
   - Program class (name, bytecode/AST, memory requirements)
   - ProcessInstance class (the running execution)
   - A simple interpreter that can:
     - Read/write files with permission checking
     - Call other programs
     - Fail gracefully when it hits memory limits
   - **Don't build the scripting language yet.** Implement a few hardcoded programs (like `cat`, `ls`, `login`) so you can test the execution model

4. **Network simulation**
   - Network class (holds all computers)
   - Connections between nodes (authenticated, success/failure logging)
   - A method like `execute_on_remote(source_computer, dest_computer, program, args)` that simulates network execution

**Output:** A Python script where you can do this:
```python
network = Network()
player_pc = network.create_computer("player")
target = network.create_computer("target")
network.connect(player_pc, target)

# Login to player PC
player_pc.login("admin", "password")

# Run a program on target (remotely)
result = player_pc.execute_remote(target, "scan", [])
print(result.output)  # Should show target's services, maybe
```

No UI. Just pure logic.

---

### Phase 2: The Scripting Language (2–3 weeks)

Now design a *very* minimal language. Hacknet's script language is tiny — that's good for you. Consider something like:

```
PRINT "Hello"
LOAD ./path/to/file
APPEND output.txt buffer
DELETE file_to_remove
RETURN
```

Very imperative, no loops, maybe no conditionals at first.

**Implement:**
1. **Lexer** (tokenize input)
2. **Parser** (turn tokens into AST)
3. **Interpreter** (walk AST, execute with permission checks)
4. Use the same execution context you defined in Phase 1

**Why Phase 2, not Phase 1?** Because once you have Phase 1 working, you can test the language against your simulated filesystem and see if it's fun. If it's not, change it. You haven't painted yourself into a corner.

**Key constraint:** Make every instruction take up a fixed amount of memory. `PRINT` costs 4 bytes, `APPEND` costs 10, etc. This forces players to think about code size.

---

### Phase 3: The Curses UI (3–4 weeks)

Now build the interface *on top of* the engine.

**Start minimal:**
- A terminal emulator window that shows a bash-like prompt
- Players type commands like `ssh target 192.168.1.5`
- Output from the simulation is printed to the terminal
- A second panel showing "memory remaining" on the current computer
- A file browser panel (navigate filesystem visually)

**Don't try to build a text editor yet.** Just have players paste code in.

The point here: your simulation should be *completely decoupled* from the UI. The curses layer is just a renderer. If you get the decoupling right, you can swap in a GUI later or even a web interface.

**Key architectural pattern:**
```python
class GameState:
    network: Network
    player_computer: Computer
    current_user: str
    
class TerminalUI:
    def __init__(self, game_state):
        self.game = game_state
    
    def execute_command(self, cmd: str):
        # Parse cmd, call game_state methods, capture output
        result = self.game.run_command(cmd)
        self.render_output(result)
```

---

### Phase 4: The Text Editor (2 weeks)

Once curses is working, add a modal text editor. Use `curses` forms or even just implement a simple line-by-line editor. Players press `edit script.hack`, edit, and press Ctrl+S to save.

This should be relatively straightforward if Phase 3 is clean.

---

### Phase 5: Game Content & Progression (4+ weeks)

Now you build the fun stuff:
- Mission objectives ("hack into this computer and steal file X")
- Capability programs that unlock later missions (infiltration tools, privilege escalation exploits, etc.)
- Realistic progression curve
- Flavor text, atmosphere

The simulation and UI are now solid — you're just adding content and game design.

---

## Scope Management & Extensibility

**To keep yourself from drowning, commit to these constraints early:**

1. **No loops in the scripting language initially.** Add them only if you find you need them. Same with conditionals.

2. **No multithreading in the simulation yet.** Programs run synchronously. This keeps the event model simple.

3. **Single-player only.** A network with one player node and N target nodes. Don't build multiplayer networking.

4. **Fixed set of permissions initially.** Just `owner`, `group`, `other` with `rwx`. Don't add ACLs.

5. **Hardcoded programs for now.** Implement a few key ones (`cat`, `ls`, `login`, `scan`). Let players write scripts on top of them, don't let them write everything.

These aren't permanent — they're guardrails while you figure out what's actually fun.

---

## Testing Strategy

Because you're building a complex simulation, **unit tests are non-negotiable**:

- Test filesystem operations (create, delete, read, write, with permission checks)
- Test the interpreter against a suite of small scripts
- Test network connectivity
- Build integration tests: "Run this quest, verify the player can complete it"

Use Python's `unittest` or `pytest`. Make your test suite small enough to run in <1 second.

---

## The Distributed Computing Layer (Future)

You mentioned wanting players to distribute scripts across multiple hacked computers to manage memory. **Don't plan for this yet.** Build it in Phase 6, after the core game is playable.

When you do, the architecture is: a program can spawn a subprocess on a *remote* computer if they're connected and authenticated. The subprocess runs asynchronously and sends results back. This unlocks the "distribute a big task" gameplay.

---

## Key Architectural Insight

**The game engine should know nothing about curses.** Your `GameState` should be a pure Python class that can be tested without a terminal. The curses UI is a *view* of that state. This separation buys you extensibility for free — you can later add a web UI, an AI that plays the game, or a replay system, and the engine doesn't care.

---

## Next Step: What to Do Right Now

Spend one week on **Phase 0.** Write a 200-line pseudocode document (or small Python prototype) that answers:
- What does a filesystem permission check look like?
- What happens when you run a program?
- How does the player compromise a node?

Once those are clear, the rest becomes implementing details. And you'll be much less likely to paint yourself into a corner halfway through.

This feels like a lot, but breaking it into phases means you have *working software* after phase 1 (just no UI), and each phase adds a single dimension of complexity. That's much better than trying to build the whole thing at once.

Does this help clarify the dependencies? Are there specific components where you're already stuck on design decisions?