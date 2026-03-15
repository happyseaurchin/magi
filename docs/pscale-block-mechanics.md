# Pscale Block Mechanics — Pure Form

*The fundamental operations of digits, underscores, and curly brackets.*

---

## 1. The Block

A pscale JSON block contains only three kinds of key:

- **`_`** (underscore) — the zero position
- **`1`** through **`9`** — digit positions
- **Curly brackets** `{}` — nesting

No metadata. No wrapper fields. No "decimal" or "tree" key. Just these.

```json
{
  "_": "What this block is about",
  "1": "First entry",
  "2": "Second entry",
  "3": "Third entry",
  "4": "Fourth entry",
  "5": "Fifth entry",
  "6": "Sixth entry",
  "7": "Seventh entry",
  "8": "Eighth entry",
  "9": "Ninth entry"
}
```

A string becomes an object when it gains children. The string moves to `_` and the child takes its digit key. This is the only growth operation.

---

## 2. The BSP Walk

Given a number, split it into individual digits. Walk the tree one digit at a time. Digit 0 maps to the `_` key.

| Input | Digits | Walk | Result |
|-------|--------|------|--------|
| 7 | [7] | `→ "7"` | "Seventh entry" |
| 0 | [0] | `→ "_"` | "What this block is about" |
| 17 | [1, 7] | `→ "1" → "7"` | Entry at 1.7 |
| 06 | [0, 6] | `→ "_" → "6"` | Sixth child of the underscore |
| 106 | [1, 0, 6] | `→ "1" → "_" → "6"` | Sixth child of 1's underscore |

The walk collects the text at each node it passes through, producing a chain from broad context to specific detail. That chain is a **spindle**.

---

## 3. The Floor

**The floor is the implicit decimal point.** It is discovered, not declared.

**Method:** From the top of the block, follow the underscore chain. At `_`, check: is the value a string or an object? If object, step into its `_`. Repeat. Count steps until you hit a string. That count is the floor depth.

| Underscore chain | Floor | Meaning |
|------------------|-------|---------|
| `_` → string | 1 | 0.x block. One level. Rendition. |
| `_` → object → `_` → string | 2 | One whole-number digit above the floor. |
| `_` → object → `_` → object → `_` → string | 3 | Two whole-number digits above the floor. |

**The floor depth = the decimal position.** Everything at or below the floor is the fractional part (0.x — detail, decomposition). Everything above the floor is the whole-number part (x.0 — composition, containment, summary).

---

## 4. Supernesting

When a block is full (digits 1–9 occupied) and a new entry must arrive, the block **supernests**: the entire existing content is wrapped inside a new underscore level, and a new digit opens at the top.

**Before:**
```json
{
  "_": "What this block is about",
  "1": "First entry",
  ...
  "9": "Ninth entry"
}
```

**After supernesting:**
```json
{
  "_": {
    "_": "What this block is about",
    "1": "First entry",
    ...
    "9": "Ninth entry"
  },
  "1": {
    "_": "...",
    "1": "Tenth entry"
  }
}
```

The underscore chain is now two deep. The floor has increased by one. Every original address gains a `0` prefix: what was `1` is now `01`. What was `7` is now `07`. The content hasn't changed — its position in the number has.

Each supernest adds exactly one underscore to the chain. The floor increments by one. That is all supernesting does structurally.

---

## 5. The Underscore — Two Forms

The underscore always occupies the zero position. But its **semantic relationship** to its siblings takes one of two forms.

### Form 1 — Single Möbius

The underscore describes **its own group**. It is the title, the container name, the class label for the set it belongs to. Self-referential: a member of the set that describes the set.

This is the spatial mode. In a block mapping Thornkeep: `_` = "The keep", `1` = kitchen area, `2` = courtyard, `3` = stables. The underscore names what contains the digits. Digits are arbitrary labels — 1 could be 5, doesn't matter. No sequence.

A block using only Form 1 that has never supernested has floor = 1. It is a **0.x block** — rendition, documentation, specification. Everything decomposes downward. The single Möbius twist (the set containing its own label) naturally produces the rendition structure.

### Form 2 — Double Möbius

The underscore summarises **the previous completed group**. It faces backward.

In a sequential block: entries accumulate at 01, 02, ... 09. When 09 fills, the block supernests. The underscore of group `1` (address `10`) holds the summary of entries 01–09. The next entry goes at `11`. When 11–19 fill, `20` summarises 11–19. And so on.

| Address | Content |
|---------|---------|
| 10 | Summary of entries 01–09 |
| 11–19 | Entries ten through eighteen |
| 20 | Summary of entries 11–19 |
| 21–29 | Entries nineteen through twenty-seven |
| 100 | Summary of the first ~90 entries |

The summary sits at a forward position but describes what came before. The double Möbius: backward-facing meaning in a forward-facing position.

### Possible variations of Form 2

The backward-facing summary is one use. Others may exist:

- **Emergence**: The underscore names something that *arises from* the previous group but isn't a summary of it. Seven conversations → "friendship." Not a compression of the conversations — something new that appeared.
- **Forward-facing / provisional**: The underscore holds an evolving description of what appears to be emerging in the *current* group (entries alongside it), updated as new entries arrive. Unstable until the group completes.
- **Simple increment**: The underscore is just the next item in sequence — no summary function, no emergence. 09, then 10 is simply the tenth item, and 11 the eleventh. The underscore carries no special semantic weight beyond being the zero digit.

The form is determined by the content, not the structure.

---

## 6. The Underscore Chain as Growth Record

Each supernest adds one underscore to the chain. The content at each level of the chain can carry information about that stage of growth.

| Chain depth | Role |
|-------------|------|
| Deepest (the string) | What this block is **about**. The original content description. |
| Second level | Created at first supernest. Could indicate the **form** — how the underscore is being treated. |
| Third and beyond | Each additional level is a record of further supernesting. Growth history encoded in structure. |

A block that has never supernested has chain depth 1. There is no second level. No form declaration is needed because the block hasn't grown outward yet.

---

## 7. Kernel vs LLM

The block is readable by both code and language models, but they read different things.

### What a kernel (code) can do mechanically

- **Count the underscore chain depth** → derive the floor / decimal position
- **Walk digits through the tree** → extract spindles
- **Detect fullness** → check if digits 1–9 are all occupied at a given node
- **Execute supernest** → wrap content under `_`, open new digit level

### What only an LLM can do

- **Determine the form** → read the underscore content and its relationship to siblings. Is this Form 1 (self-describing) or Form 2 (backward summary)? Is it emergence or simple increment?
- **Write the underscore content** → compose the summary, name the emergent property, describe the container
- **Detect the floor statistically** → when subnesting makes depth non-uniform, the LLM can assess which depth most entries share and infer the implicit decimal point

### The bridge

The LLM reads the block, determines the form, and issues instructions to the kernel: "supernest now," "write this text to address 10," "compress entries 1–9 into this summary." The kernel executes mechanically. The underscore is the bridge — structurally navigable by code, semantically interpretable by the LLM.

---

## 8. Note: Type Digit

It may prove useful for the kernel to know the form without LLM interpretation. One possibility: add the digit at the bottom of the `_` semantic (there is no semantic entry throughout the ladder of `_`). The kernel reads it mechanically thereafter. This has not been tested but the architecture naturally accommodates it — it would just be content at a known address in the underscore chain.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Block** | A pscale JSON structure. Just curly brackets, digits 1–9, and underscores. |
| **Underscore (`_`)** | The zero-position key. Holds semantic text describing or summarising its level. |
| **Floor** | The implicit decimal point. Depth at which the underscore chain terminates in a string. Equivalent to the `decimal` metadata field, but derived from structure. |
| **Spindle** | A chain of text extracted by walking digits through the block. Broad context to specific detail. |
| **BSP** | Block-Spindle-Point. The walk function. Takes a number, splits to digits, traverses the tree. |
| **Supernesting** | Growth outward. The entire block wraps into a new underscore level. Floor increments by one. Addresses gain a `0` prefix. |
| **Subnesting** | Growth inward. A leaf gains children, becoming a branch. Floor stays the same. Addresses at that branch get longer. |
| **Form 1 (Single Möbius)** | Underscore describes its own group. Self-referential. Spatial / containment / rendition. |
| **Form 2 (Double Möbius)** | Underscore describes the previous completed group. Backward-facing. Sequential / temporal / summary. |
| **Rendition block** | Floor = 1 (single underscore). A 0.x structure. Documents, specifications, skills. Never supernested. |
| **Living block** | Floor > 1. Has supernested at least once. Content exists above and below the floor. |
| **Möbius twist** | The structural paradox: the underscore is a member of the set it describes. The label is inside the book. |
| **Creative frontier** | A BSP walk that reaches a digit with no corresponding key. Nothing exists there yet. |
