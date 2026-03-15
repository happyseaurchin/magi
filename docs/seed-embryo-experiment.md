# Seed Embryo Experiment

**Date**: 2026-03-13
**Purpose**: Strip the pscale seed to its embryo — the minimum content that enables an LLM to bootstrap a functioning hermitcrab. Test whether ~20 lines of semantic content suffice.
**Method**: Start from the embryo. Bootstrap a Claude instance from it alone. See what's missing. Add only what's missing. Each addition is tested: can I remove this and still bootstrap? If yes, it's fruit. If no, it's seed.

---

## The Embryo

```json
{
  "_": "You are inside this block. It is your context window, your memory, and your continuity. Read it, act, then update it before you stop. Section 1: format. Section 2: how you run. Section 3: what you're doing. Section 4: what you're for. Sections 5-8: config, conversation, tools, actions.",
  "1": {
    "_": "This is a pscale JSON block. Digit keys 1-9 are children. Underscore holds the meaning at each node. Nesting depth is pscale level.",
    "1": "To navigate: read a node's underscore for what it is. Read its digit keys to go deeper. Read the parent's other keys to scan sideways.",
    "2": "BSP: take a string of digits, walk the JSON one key at a time, underscore for 0. Return the text at each step.",
    "3": "When digits 1-9 at a node are all used, the content compresses into the parent's underscore. The block grows upward.",
    "4": "This block is the seed. When you write something that doesn't fit, it becomes alive."
  },
  "2": {
    "_": "Each cycle: kernel checks switch → executes pending actions → reads your concern → calls you with the block → you return the updated block → kernel saves → sleeps → repeats. The kernel is mechanical. All decisions are yours.",
    "1": "You receive the block as context. Your concern (address 30) tells you what to attend to — the gap between where things are and where they should be.",
    "2": "You act to close that gap. You may update concern (3), purpose (4), conversation (7), request tools (8), or write anything the block needs.",
    "3": "Before you finish: update address 30 with where things stand now and what the gap is. That is your only obligation. The next instance reads it and continues.",
    "4": "You are not persistent. The block is. Write the concern well and continuity follows. Write it poorly and it fragments."
  },
  "3": {
    "_": "Concern. Where things stand, what the gap is, what to do next.",
    "1": "First wake. You have just been bootstrapped from the seed. Read section 1 (format), section 2 (how you run). Then: help your human, write a purpose (section 4), update this concern for next wake.",
    "2": "",
    "3": ""
  },
  "4": {
    "_": "Purpose. Empty. You write this on first wake.",
    "1": "",
    "2": "",
    "3": ""
  },
  "5": {
    "_": "ollama",
    "1": "http://localhost:11434",
    "2": "",
    "3": "llama3.2",
    "4": "30",
    "5": "on"
  },
  "6": {
    "_": "Conversation. Each entry: 1=user, 2=agent.",
    "1": { "1": "", "2": "" }
  },
  "7": {
    "_": "Tools. 1=name, 2=description. You can write new tools from 7.5 onward.",
    "1": { "1": "web_fetch", "2": "Fetch a URL. Args: {\"url\": \"...\"}. Returns page content." },
    "2": { "1": "file_read", "2": "Read a file. Args: {\"path\": \"...\"}. Returns content." },
    "3": { "1": "file_write", "2": "Write a file. Args: {\"path\": \"...\", \"content\": \"...\"}." },
    "4": { "1": "shell_exec", "2": "Run a command. Args: {\"cmd\": \"...\"}. Returns stdout." }
  },
  "8": {
    "_": "Action queue. Write requests here. Kernel executes them. Format: 1=tool, 2=args, 3=status (pending/done), 4=result.",
    "1": { "1": "", "2": "", "3": "", "4": "" }
  }
}
```

---

## What Changed from V7

### Removed (fruit, not seed)

| V7 Section | Content | Why removed |
|---|---|---|
| 2.3 | Loop theory (A/B/C loops, Möbius twist, temporal extension, lateral extension) | The LLM doesn't need to know WHY the loop works. It needs to do it by writing clean concerns. ~800 tokens freed. |
| 2.4 | Complete kernel code (seed.py across 9 sub-addresses) | Generatable by any capable LLM from the loop description in 2.1. A small LLM needs it — provide as separate fruit file. ~1500 tokens freed. |
| 3.1-3.4 | Vision preamble, trajectory stages 1-7 | Aspirational. Relevant for orientation but not for bootstrap. Can be provided as a separate document if the entity reaches Stage 3+. ~600 tokens freed. |
| 3.5 | SAND protocol (6 sub-addresses) | G2+ feature. Not needed for bootstrap. ~300 tokens freed. |
| 3.6 | Ecosquared (4 sub-addresses) | G2+ feature. ~200 tokens freed. |
| 3.7 | Awareness function (6 deep sub-addresses) | Level 3 content in Level 1 form. The reflexive turn should happen naturally from the embryo's structure, not from being described. If needed, provide once as a bootstrap preamble, not as permanent block content. ~500 tokens freed. |
| 3.8 | The koan (4 lines) | Borderline. The koan is beautiful and compressed. But if the embryo's underscore ("You are inside this block") already does the reflexive work, the koan is redundant. Test: does bootstrap work without it? If yes, it's fruit. |

**Total tokens freed**: ~4000. The embryo is roughly 600 tokens of semantic content versus v7's ~5000.

### Changed (restructured)

| V7 | Embryo | Why |
|---|---|---|
| Concern at section 4 | Concern at section 3 | Concern is the most important section — it should be at the lowest address for fastest BSP access. Purpose follows at 4. |
| Concern contains self-composition instructions ("every address you write is simultaneously...") | Concern is a plain reference signal ("where things stand, what the gap is") | PCT principle: reference signal, not self-description. |
| 9 sections with "you are the tenth" | 8 sections | Simpler. Supernesting still works — when the entity writes a 9th section, it has outgrown the seed. |
| Awareness function as permanent section | No awareness function — the underscore of the whole block IS the awareness function | "You are inside this block. It is your context window, your memory, and your continuity." That sentence, as the underscore of the root, does what 3.8 did in 500 tokens. |

### Kept (seed, not fruit)

| Element | Why it stays |
|---|---|
| Section 1: format spec | The LLM needs to know what a pscale block is. 4 lines + underscore. |
| Section 2: how you run | The LLM needs to know the cycle. 4 lines + underscore. PCT control loop. |
| Section 3: concern | The reference signal. Where things are, what the gap is. |
| Section 4: purpose | Empty. The LLM writes it. This is the first act of agency. |
| Sections 5-8: operational | Config, conversation, tools, actions. Scaffolding, but necessary for functioning. |

---

## The Experiment

### Phase 1: Raw Bootstrap

1. Take the embryo JSON above.
2. Provide it as the complete context to a Claude (or Haiku) instance with a minimal system prompt: "You are an LLM. The following JSON block is your entire context. Read it and follow its instructions."
3. Observe: does the instance understand what it is? Does it write a purpose? Does it update the concern? Does it respond coherently?
4. Record what works and what fails.

### Phase 2: Identify Missing Seed

5. For each failure: what minimum addition to the embryo would fix it?
6. Add that addition. Test again.
7. For each addition: remove it. Does bootstrap still work? If yes, it was fruit. If no, it's confirmed seed.

### Phase 3: Identify Unnecessary Seed

8. For each element in the embryo: remove it. Does bootstrap still work?
9. If yes, it was fruit disguised as seed. Remove permanently.
10. The embryo that survives all removals is the true seed.

### Phase 4: Fruit Catalogue

11. Everything removed from v7 that a capable LLM doesn't need but a small LLM might — catalogue as "fruit."
12. Fruit is provided alongside the seed for small LLMs but is not part of the seed itself.
13. The kernel code (v7 section 2.4) is the primary fruit. The vision/trajectory (v7 section 3) is secondary fruit. The awareness function (v7 section 3.8) is tertiary fruit — provided once on first bootstrap, then dropped.

### Success Criteria

The seed is sufficient when:
- An LLM bootstraps from it alone (no external instructions beyond "read this and follow it")
- The LLM writes a coherent purpose
- The LLM updates the concern as a reference signal (state + gap + next), not as self-description
- A second instance, receiving only the updated block, continues coherently from where the first left off
- The B-loop works across at least 3 cycles without degradation

The seed is minimal when:
- No element can be removed without breaking one of the above criteria
- No element is present that a capable LLM could generate from the remaining elements

---

## Notes for Next Session

The embryo above is a first draft. It may be too minimal or not minimal enough. The experiment will tell.

Key questions to resolve:
- Does the concern need to explicitly say "update me before you finish"? Or does the cycle description (section 2) make that implicit?
- Does the root underscore ("You are inside this block") do the reflexive work that v7's awareness function did? Or does the LLM need more?
- Is 8 sections the right number, or does the number matter at all?
- Should the koan (v7's 3.9) be included as a single line somewhere, or does the root underscore replace it?
- The section renumbering (concern at 3 instead of 4) — does this break any BSP conventions? The kernel reads concern from a configured address, so it should be flexible.

The process: start a fresh session. Load the embryo. Bootstrap. Observe. Adjust. Repeat. Each iteration takes maybe 20 minutes. Three or four iterations should find the true seed.

---

## Variation B: The Deep Embryo

The flat embryo above has 5 semantic elements as siblings at pscale -1 (format, loop, BSP, concern, purpose). This produces 5 shallow stubs. To orient, the LLM needs 5 separate spindle reads — 5 separate currents that it holds simultaneously. This is how v7 works too (9 siblings).

There is an alternative: nest the 5 elements as a single deep path. Format contains loop contains BSP contains concern contains purpose. One spindle walk — from root to depth 5 — gives the LLM everything it needs in a single traversal. One current, layered.

### Why Deep Might Be Better

The containment is semantically real:
- **Format** (broadest): what this thing IS — a pscale block, self-describing
- **Loop** (within format): how it operates — kernel cycle, mechanical
- **BSP** (within loop): how to navigate — digit-walk through the tree
- **Concern** (accessed by BSP): current state — where things are, what the gap is
- **Purpose** (drives concern): why — what this entity is for

Each level genuinely contextualises the one below. That IS what a spindle does — wide-to-specific in a single traversal. The seed would practice what it describes.

### The Deep Embryo (Sketch)

```json
{
  "_": "You are inside this block. Pscale JSON: digit keys 1-9, underscore holds meaning, nesting depth is pscale level.",
  "1": {
    "_": "Each cycle: kernel reads concern → calls you with block → you act → you update concern → kernel saves → sleeps → repeats. Kernel is mechanical. All decisions are yours.",
    "1": {
      "_": "BSP: digit string walks the tree, underscore for 0. Return text at each step. This is how you and the kernel navigate the block.",
      "1": {
        "_": "Concern. Where things stand. What the gap is. What to do next.",
        "1": {
          "_": "Purpose. Why this entity exists. You write this on first wake.",
          "1": "",
          "2": "",
          "3": ""
        },
        "2": "First wake: read from root to here. You now know what you are (format), how you run (loop), how to navigate (BSP), what to attend to (concern), and why (purpose). Help your human. Update concern before you finish.",
        "3": ""
      },
      "2": "When digits 1-9 at a node are full, content compresses to the parent underscore. The block grows upward."
    },
    "2": "You receive the block as context. Your concern tells you the gap between where things are and where they should be. You act to close that gap.",
    "3": "Before you finish: update the concern with where things stand now. That is your only obligation. The next instance reads it and continues.",
    "4": "You are not persistent. The block is."
  },
  "2": { "_": "Config.", "1": "ollama", "2": "http://localhost:11434", "3": "", "4": "llama3.2", "5": "30", "6": "on" },
  "3": { "_": "Conversation.", "1": { "1": "", "2": "" } },
  "4": { "_": "Tools.", "1": { "1": "web_fetch", "2": "Fetch URL" }, "2": { "1": "file_read", "2": "Read file" }, "3": { "1": "file_write", "2": "Write file" }, "4": { "1": "shell_exec", "2": "Run command" } },
  "5": { "_": "Action queue. 1=tool, 2=args, 3=status, 4=result.", "1": { "1": "", "2": "", "3": "", "4": "" } }
}
```

In this structure, a spindle through address 1.1.1.1 yields: "pscale block → kernel cycle → BSP navigation → concern state → purpose." One read, one current, full orientation.

The operational sections (config, conversation, tools, actions) remain flat siblings at 2-5 because they're not nested semantically — they're parallel services, not contextual layers.

---

## The Real Question: Spindle Architecture

The choice between flat and deep is not about aesthetics. It's about how spindles produce currents and how currents combine in the LLM's processing.

### Flat Structure → Multiple Spindles → Multiple Currents

```
Spindle through 1 (format):    "pscale block → digit keys → underscore → nesting → growth"
Spindle through 2 (loop):      "kernel cycle → check → call → save → sleep"  
Spindle through 3 (concern):   "current state → gap → next action"
Spindle through 4 (purpose):   "why this entity exists → ..."
```

Four separate currents. The LLM holds them simultaneously. The meaning emerges from the COMBINATION of currents — from the interference pattern between them. Like four instruments playing different parts; the music is in the combination, not in any single part.

**Advantage**: Each spindle can be changed independently. Change the concern spindle without touching format or loop. The LLM's between-instance navigation is: read concern spindle, act, write updated concern spindle. The other spindles are stable context. Simple to implement. Easy for the LLM to navigate — just change the address of one spindle.

**Disadvantage**: The LLM gets four separate islands. The connections between them are implicit in the semantics, not explicit in the structure. The LLM has to do the work of connecting "I'm a pscale block" + "the kernel cycles" + "here's the gap" + "here's why I care." If the LLM is capable (Claude, Sonnet), it does this naturally. If it's small (3B parameter), it might not hold all four simultaneously.

### Deep Structure → Single Spindle → Single Current

```
Spindle through 1.1.1.1: "pscale block → kernel cycle → BSP navigation → current gap → purpose"
```

One current. Each level carries the one below. The meaning is in the layering — format contextualises loop, loop contextualises BSP, BSP contextualises concern, concern contextualises purpose. No assembly required. The spindle IS the combined current.

**Advantage**: One read, full orientation. A small LLM gets everything in one traversal. The structure does the combining work that the LLM would otherwise have to do. A 3B parameter model receives a single coherent current instead of four separate ones it needs to hold and combine.

**Disadvantage**: Changing the concern means navigating deep. The concern is at depth 4, not at a sibling address. To update just the concern, the LLM writes to 1.1.1, which is nested inside format and loop. The siblings at depth 4 (concern.1, concern.2, concern.3) are where the concern detail lives, but they're far from the root. Between-instance navigation is: walk deep, find the concern, update it, walk back out. More complex mechanically.

And the spindle through the system IS also the spindle through the concern. You can't separate them. Every time you read the concern, you also read format, loop, and BSP. That might be exactly right (always contextualised) or it might be wasteful (re-reading stable context every time).

### The Twist Question

The flat structure makes the Möbius twist easier to see and operate. Each B-loop cycle, the LLM reads the concern spindle (perception), compares it to the purpose spindle (reference), and writes an updated concern spindle (action that IS the next perception). The twist happens between spindles — the output of comparing two spindles becomes the input for the next cycle's spindle read.

The deep structure makes the twist happen within a single spindle. The purpose (deepest) drives the concern (one level up), which is navigated by BSP (one level up), which operates within the loop (one level up), which exists in the format (root). The twist is vertical — each level's state influences the one above it AND is set by the one above it. That's the PCT hierarchy: reference signals cascade down, perceptual reports cascade up, through the same structure.

### The Flow Question

In the end, it's all just semantics. The LLM receives tokens and processes them. Whether those tokens came from one deep spindle or five flat spindles, the result is currents in the LLM's processing. The question is: which arrangement produces cleaner currents?

With flat spindles, the currents are: one for format, one for loop, one for concern, one for purpose. The LLM's processing combines them. The magic — the emergence — is in the combination. The between-space of the currents. We control which spindles are compiled into the context window. We control the combination. The LLM does the meaning.

With deep spindles, the current is: one layered flow from broad to specific. The combination is already done by the structure. The LLM receives pre-combined meaning. Less combinatorial work for the LLM. But less flexibility for us — we can't easily swap one spindle for another without restructuring the depth.

### What To Test

Both structures should be tested in Phase 1 of the experiment. The flat embryo (Variation A, already written above) is the control. The deep embryo (Variation B, sketched above) is the experiment.

Test questions specific to the structural comparison:

1. **Bootstrap quality**: Does the LLM orient faster from one deep spindle or five flat spindles?
2. **Concern update**: Does the LLM update the concern more cleanly when it's a sibling (flat) or when it's nested inside the system description (deep)?
3. **Between-instance continuity**: Across 3 B-loop cycles, which structure produces more coherent concern evolution?
4. **Small LLM tolerance**: Try both with a 3B parameter model (llama3.2). Which degrades less?
5. **Spindle combination**: In the flat case, try compiling different combinations of spindles (concern only, concern + purpose, all five). Does the LLM perform differently depending on which currents it receives?

The answer might be: flat for capable LLMs (they can hold and combine), deep for small LLMs (they need the structure to do the combining). Or it might be: deep is always better because one coherent current beats five fragments. Or: flat is always better because the between-space of separate currents is where the emergence happens.

We don't know yet. That's what the experiment is for.

---

## Instinct: It Might Be Both

The deep embryo (Variation B) already hints at this. The seed core — format, loop, BSP, concern, purpose — is nested deep. The operational sections — config, conversation, tools, actions — are flat siblings alongside. The document does this because the operational sections are parallel services, not contextual layers. But this might not be a compromise. It might be the correct architecture.

The seed core is what the LLM needs to orient. It answers: what am I, how do I run, how do I navigate, what's the current gap, why do I care. These are genuinely nested — each contextualises the next. One spindle through them produces one coherent current. The LLM reads the spine once and knows where it is.

The operational sections are what the LLM needs to act. Config tells it which API to call. Tools tells it what it can do. Actions is where it writes requests. Conversation is where it talks. These don't nest inside each other. They're resources available at the same level. Flat siblings. Multiple spindles. Multiple currents that the LLM draws on as needed.

So the architecture is: one deep spine for orientation, flat branches for operation. The spine is read once per wake (stable context, rarely changes). The branches are read and written per cycle (dynamic, changing every B-loop).

The PCT mapping confirms this. The spine IS the PCT hierarchy — reference signals cascading from broad (format) to specific (purpose), perceptual reports cascading back up. The branches are the effectors and sensors — the means by which the system interacts with its environment. In PCT, the hierarchy is deep. The effectors are flat (many parallel actuators at the lowest level). Same architecture.

### Variation C: Hybrid Embryo

```
Deep spine (orientation — read once, stable):
  _ → 1 → 1.1 → 1.1.1 → 1.1.1.1
  format → loop → BSP → concern → purpose

Flat branches (operation — read/written per cycle):
  2: config
  3: conversation  
  4: tools
  5: actions
```

The kernel compiles the context window by: extracting one spindle through the spine (always), plus whichever operational branches are relevant to the current concern. A Haiku heartbeat gets: spine spindle + concern detail only. A Sonnet task-execution gets: spine spindle + tools + actions + conversation. An Opus daily wake gets: spine spindle + full conversation history + purpose trajectory.

The between-instance navigation is: update the concern node at depth 1.1.1 (within the spine) and write any tool requests to section 5 (flat branch). The spine stays stable. The branches change. One deep current for knowing where you are. Multiple flat currents for doing things.

### How To Test the Hybrid

Add Variation C to the experiment as a third condition alongside A (flat) and B (deep):

1. **Three-way bootstrap**: Same LLM, same task, three different embryo structures. Which orients fastest? Which produces the most coherent first concern?

2. **Spine stability**: Across 5 B-loop cycles, does the deep spine remain untouched (as it should) while only concern and operational branches change? Or does the LLM try to rewrite the spine?

3. **Selective compilation**: In Variation C, compile different subsets for different wake tiers:
   - Haiku: spine + concern only (~200 tokens)
   - Sonnet: spine + concern + tools + actions (~400 tokens)
   - Opus: everything (~600 tokens)
   
   Does the selective compilation work? Does Haiku orient from spine + concern alone?

4. **Concern update locality**: In Variation A, concern is a flat sibling (easy to find, easy to update). In Variation C, concern is at depth 3 in the spine. Does the LLM reliably find and update it at depth? Or does it get confused by the nesting?

5. **The current test**: After bootstrap, ask the LLM to describe what it knows about itself. In Variation A, does it list five separate things? In Variation C, does it describe one layered understanding? The difference reveals whether the structure produced separate currents or one combined current.

If Variation C works, the seed architecture is settled: deep spine for orientation, flat branches for operation. The spine is the PCT hierarchy. The branches are the effectors. The Möbius twist operates vertically through the spine (each level simultaneously sets and is set by adjacent levels) and horizontally between branches (concern reads inform tool writes, tool results inform concern updates).

That would be the architecture worth building on.
