# ComfyUI Expression Nodes

Custom nodes for automating expression generation and outfit changes in ComfyUI workflows.

## Installation

Place this repository in `ComfyUI/custom_nodes/expression_nodes` and restart ComfyUI. The nodes appear under `ExpressionNodes`. No additional Python dependencies are required by this package.

## Features

### Sprite Prompt Generator
One prompt node for reference-based sprite creation, expression batches, and touch-up edits. Restart ComfyUI after installing or updating these nodes.

- `mode`: **Base** produces a neutral base prompt, **Expressions** produces the expression list, and **Edit** produces a touch-up prompt.
- `character_name`: Used for image and archive names, e.g. `Blair_Joy` and `Blair Expressions`.
- `base_prompt`, `expression_template`, `edit_prompt`: Editable instructions for each mode.
- `style`: Shared instructions appended to the selected prompt.
- `face_detail`: Replaces `{face detail}` or `{face_detail}`; appended when neither placeholder is present.
- `expressions`: Blank uses the original 28 expressions in their original order. Otherwise enter one per line, optionally as `Joy | a broad happy smile` to separate the filename from the expression description.
- `additional_expressions`: Appends custom entries after the default 28 or your selected `expressions`. Uses the same `Name | description` format; descriptions replace `{expression}` in the template and receive the shared style and face details. Only used in Expressions mode. Blank lines are ignored and duplicate filenames receive suffixes.
- `repeats`: Variants per expression/base/edit. Repeated filenames get `_01`, `_02`, etc.
- `seed`: Each repeat increments the seed. The same repeat uses the same seed across expressions.

For example, leave `expressions` blank and enter this in `additional_expressions` to generate 30 expressions:

```text
Wink | a playful wink with a small smile
Determined | narrowed eyes and a confident determined smile
```

Outputs:

| Output | Description |
| --- | --- |
| `prompts` | Formatted prompts for the selected mode |
| `filenames` | Matching names for each generated prompt |
| `archive_name` | A single name combining the character and mode |
| `seeds` | Matching seeds for each prompt and repeat |

Prompts, filenames, and seeds are aligned ComfyUI lists.

Choose **Base** for a neutral character prompt, **Expressions** for an expression batch, or **Edit** for touch-up instructions. Edit the expression template if you also want pose changes.

### 1. Expression Generator (28)
Generates a batch of 28 distinct facial expressions (Admiration, Joy, Anger, etc.) from a single prompt template.
-   **Inputs**:
    -   `template`: Text template (e.g., "Change expression to {expression}...").
    -   `face_detail`: Additional details (e.g., "green eyes").
-   **Outputs**:
    -   `prompts`: List of formatted prompts.
    -   `expression_names`: Keys for filenames.

### 2. Outfit Generator (Expressions, 28 Inputs)
Designed for processing existing expression images with manual mapping.
-   **Inputs**:
    -   `prompt`: The prompt to use (e.g., "changing outfit to Space Suit").
    -   `repeats`: Number of variations per image.
    -   `Admiration`, `Joy`, etc.: Connect specific images.
-   **Outputs**:
    -   `prompts`: The prompt, repeated match the batch size.
    -   `filenames`: Expression names (e.g., "Joy", "Anger"). Repeats reuse the same name.

### 3. Outfit Generator (Batch)
Generic batch processor.
-   **Inputs**:
    -   `images`: Batch input.
    -   `outfit_name`: String.
