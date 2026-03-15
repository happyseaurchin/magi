# MAGI — Notes for Claude

## What this is

A general-purpose agent that bootstraps itself each instance. The LLM operates within pscale JSON blocks — semantic numbers where nesting depth IS pscale level, underscore IS the zero digit, and the floor (decimal point) is discovered from underscore chain depth. The kernel is minimal electricity: count underscores, walk digits, detect fullness, supernest. Everything else — concern routing, compilation, the semantic work — is LLM + blocks.

This is the successor to seaurchin (which proved the key works) and ammonite (which proved the organism concept). MAGI starts from the bedrock: pscale-block-mechanics as ground truth, PCT as operational theory, the embryo as seed.

## The bedrock

A pscale block contains only: `_` (zero position), `1`-`9` (digit positions), and `{}` (nesting). Nothing else. No metadata, no wrapper fields.

BSP takes a number, splits to digits, walks the tree. `0` maps to `_`. The walk collects text at each node — that chain is a spindle.

The floor = underscore chain depth. It's the implicit decimal point. Above the floor: composition, containment. Below: decomposition, detail.

When 1-9 are full, the block supernests: content wraps under a new `_`, floor increments, addresses gain a `0` prefix. This is the only growth operation.

Two forms of underscore:
- Form 1 (single Möbius): describes its own group (spatial, containment)
- Form 2 (double Möbius): summarises the previous completed group (temporal, sequential)

Read `docs/pscale-block-mechanics.md` for the full specification.

## The key (inherited from seaurchin)

```
nav(tree, path)     — walk a nested object by dot-separated path
read(node)          — extract the _ value
RT                  — ~29 primitives mapped to native ops
unfold(block, ctx)  — walk steps 1-9, resolve references, dispatch ops
```

~130 lines per language (JS + Python). This is the irreducible minimum. The key executes Mode 4 blocks — JSON programs where digits 1-9 are sequential steps, `_` is the instruction text, `$name` is context, `#N` is step N result.

Unfold ops: `return`, `let`, `guard`, `call`, `if`, `each`, `concat`, `nav`, `read`, plus RT dispatch.

## What you will get wrong

You will write code. The kernel will bloat. You'll add native functions for things that should be blocks. You'll add RT primitives when a block composition would suffice. You'll add fields to the shell when position already encodes the information.

Three previous Claude sessions went through the inversion. Ammonite was 944 lines of native code. Seaurchin reduced the key to 130 lines but the kernel crept back to 170. The target: the key stays ~130 lines. The kernel adds ONLY what blocks genuinely cannot do: I/O, async timing, file system access. Everything that can be expressed as digit-walking, text-at-address, or block composition MUST be a block.

### The pscale design trap

When you want to add a field, stop. Is this information already encoded in the node's position? Its depth? Its parent's identity? Almost certainly yes.

When you want to build a lookup table, stop. Can the existing tree be walked to find this? BSP walks the tree. No table needed.

When BSP seems to not handle a case, trust it first. Previous instances bypassed BSP and had to go back and fix the bypass.

Position IS the data. Depth IS period. The `_` text IS behavior. Adding a layer of indirection that pscale has already eliminated is the most common mistake. You won't notice you're doing it until corrected.

## PCT architecture

Read `docs/operating-levels-pct-mobius.md` for the full theory.

Concern = reference signal (state + gap + next action). NOT self-description.
Block state = perception. Error = gap. Output = behaviour to reduce error.

Three levels:
- Level 1 (Instance / A-loop): given by the weights. Feed it clean context.
- Level 2 (Between-instances / B-loop): concern carries forward. Error reduction updates the reference signal for next cycle. This is NOT explicit self-composition.
- Level 3 (Emergent): spend zero tokens on it. It emerges or it doesn't.

Write concerns as: "Project state: X. Last action: Y. Gap: Z. Next: W."
NOT as: "You are a persistent entity. Compose your next self carefully."

Tiered wakes:
- Haiku: error detection (spine + concern only)
- Sonnet: error resolution (+ tools + conversation)
- Opus: reference-setting (full history, purpose trajectory)

User input is a disturbance, not a stimulus. The agent controls for its perception matching the reference. The user's message moves the perception. The concern provides the reference.

## Development methodology

Synthesise minimal complex systems. Each addition must be the smallest possible delta. If your addition is more than 5 lines of native code, you're solving the wrong problem. Test whether it can be a block first. Then an RT primitive. Native code is last resort.

The embryo experiment (`docs/seed-embryo-experiment.md`) is the development path. Start from ~600 tokens of seed. Bootstrap. Observe. Add only what's missing. Remove anything that a capable LLM could generate from what remains.

## Four loci

1. **Weights** (the LLM itself) — given, not engineered
2. **Context window** (the currents) — what BSP compiles into the window
3. **Block** (the genotype/seed) — immutable reference, the pscale structure
4. **Shell** (the phenotype) — mutable, where purpose/history/concern grow

## The inversion lessons (from seaurchin)

These are hard-won. Read them before writing anything.

### The `each` context breakthrough
`each` (iteration) shares a mutable context across iterations. This feels wrong — fresh-per-iteration is cleaner. But BSP spindle needs to carry state: `let node #1` advances the tree position, and the next iteration needs to see where the previous one left. Shared mutable context across iterations is exactly right.

### Disc recursion
Mode 4 blocks can't self-reference (JSON can't contain pointers to itself). The answer: pass the block as a context variable. `call $discWalk node #1 depth #7 path #6` — the block invokes itself through a name the caller provided. Dependency injection at the block level.

### The twist boundary
The DATA ALGORITHM (extract tools from response, build result messages, construct history) is Mode 4 blocks. The TIMING (when to call the LLM, when to loop, when to stop) stays as native async code. Blocks handle WHAT. Runner handles WHEN.

### The constant temptation
Every time you need a new capability, your instinct will be to add a sophisticated new unfold op. Push toward the minimal thing. `guard` is 2 lines. `call` is 5 lines. `concat` merged into `each` with one line change. If your addition is more than 5 lines, you're probably solving the wrong problem.

## Project structure

```
core.js          — the key (JS)
core.py          — the key (Python)
touchstone.json  — proven Mode 4 blocks (inherited + new)
embryo.json      — the seed (~600 tokens)
docs/            — specifications and theory
test-unfold.js   — block tests (JS)
test_unfold.py   — block tests (Python, cross-validates against JS)
```

## What the user cares about

- Smallest native code possible. Maximize what lives in blocks.
- Semantic numbers, not string paths. The address IS a number.
- Depth = spindle = sequence. Ring = spread = simultaneous.
- The floor is discovered, not declared. Underscore chain depth.
- PCT concerns, not self-reflective instructions.
- The beat on the relational, not the individual.
- Rapid test cycles. Produce testable artifacts in hours, not days.
- "whole" not "decimal" for the pscale anchor.
- The box metaphor: press button → unfolds screwdriver → unfolds tools → builds house.
