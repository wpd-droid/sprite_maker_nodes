import re


EXPRESSIONS = (
    "Admiration", "Amusement", "Approval", "Caring", "Desire",
    "Excitement", "Gratitude", "Joy", "Love", "Optimism", "Pride", "Relief",
    "Anger", "Annoyance", "Disappointment", "Disapproval", "Disgust",
    "Embarrassment", "Fear", "Grief", "Nervousness", "Remorse", "Sadness",
    "Confusion", "Curiosity", "Neutral", "Realization", "Surprise",
)


def filename_part(text):
    return re.sub(r'[\\/:*?"<>|,\x00-\x1f%]', '_', text).strip(' .') or "sprite"


class SpritePromptGenerator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Expressions", "Base", "Edit"],),
                "character_name": ("STRING", {"default": ""}),
                "repeats": ("INT", {"default": 1, "min": 1, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "face_detail": ("STRING", {"default": ""}),
                "style": ("STRING", {"multiline": True, "default": "Black outline. Transparent background."}),
                "base_prompt": ("STRING", {"multiline": True, "default": "Create a full body colored portrait of the reference character, with a neutral expression and pose looking forward. Preserve the character's identity and clothing. Remove non clothing graphics and objects held in hand. Keep the whole character in frame."}),
                "expression_template": ("STRING", {"multiline": True, "default": "Change the facial expression to {expression}. Preserve the character's identity, clothing, pose, framing, and scale."}),
                "edit_prompt": ("STRING", {"multiline": True, "default": "Remove unwanted marks. Preserve the character's identity, mouth, clothing, pose, framing, and scale."}),
                "expressions": ("STRING", {"multiline": True, "default": "", "tooltip": "Blank uses all 28 expressions. Otherwise one per line: Joy or Joy | a broad happy smile."}),
                "additional_expressions": ("STRING", {"multiline": True, "default": "", "tooltip": "Append to the default or selected expressions. One per line: Wink | a playful wink. Descriptions replace {expression} in the expression template."}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("prompts", "filenames", "archive_name", "seeds")
    OUTPUT_IS_LIST = (True, True, False, True)
    FUNCTION = "generate"
    CATEGORY = "ExpressionNodes"

    def generate(self, mode, character_name, repeats, seed, face_detail="", style=None,
                 base_prompt=None, expression_template=None, edit_prompt=None, expressions="",
                 additional_expressions=""):
        defaults = self.INPUT_TYPES()["optional"]
        if style is None:
            style = defaults["style"][1]["default"]
        if mode == "Expressions":
            template = expression_template if expression_template is not None else defaults["expression_template"][1]["default"]
            entries = []
            lines = expressions.splitlines() if expressions.strip() else list(EXPRESSIONS)
            lines.extend(additional_expressions.splitlines())
            for line in lines:
                if line.strip():
                    name, separator, description = line.strip().partition("|")
                    entries.append((name.strip(), description.strip() if separator else name.strip()))
        elif mode == "Base":
            template = base_prompt if base_prompt is not None else defaults["base_prompt"][1]["default"]
            entries = [("base", "Neutral")]
        elif mode == "Edit":
            template = edit_prompt if edit_prompt is not None else defaults["edit_prompt"][1]["default"]
            entries = [("edit", "Neutral")]
        else:
            raise ValueError(f"Unknown sprite prompt mode: {mode}")

        prompts, filenames, seeds = [], [], []
        used_names = set()
        prefix = filename_part(character_name) + "_" if character_name.strip() else ""
        for name, description in entries:
            prompt = " ".join(part.strip() for part in (template, style) if part.strip())
            has_face_detail = "{face detail}" in prompt or "{face_detail}" in prompt
            prompt = prompt.replace("{expression}", description).replace("{face detail}", face_detail).replace("{face_detail}", face_detail)
            if face_detail.strip() and not has_face_detail:
                prompt = f"{prompt} Character details: {face_detail.strip()}".strip()
            for repeat in range(repeats):
                suffix = f"_{repeat + 1:02d}" if repeats > 1 else ""
                filename = prefix + filename_part(name) + suffix
                unique_name = filename
                counter = 2
                while unique_name.casefold() in used_names:
                    unique_name = f"{filename}_{counter}"
                    counter += 1
                used_names.add(unique_name.casefold())
                prompts.append(prompt)
                filenames.append(unique_name)
                seeds.append((seed + repeat) % (1 << 64))

        archive_name = filename_part(f"{character_name.strip()} {mode}".strip())
        return (prompts, filenames, archive_name, seeds)

class ExpressionGenerator:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "template": ("STRING", {
                    "multiline": True,
                    "default": "Change expression to {expression} and ensure {face detail}, this expression is cute"
                }),
                "face_detail": ("STRING", {
                    "default": ""
                }),
                "repeats": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompts", "expression_names")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "generate_expressions"
    CATEGORY = "ExpressionNodes"

    def generate_expressions(self, template, face_detail, repeats):
        expressions = EXPRESSIONS

        prompts = []
        expression_names = []

        for expression in expressions:
            current_prompt = template.replace("{expression}", expression).replace("{face detail}", face_detail)

            for _ in range(repeats):
                prompts.append(current_prompt)
                expression_names.append(expression)

        return (prompts, expression_names)

class OutfitGenerator:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "outfit_name": ("STRING", {
                    "default": "Red Dress",
                    "multiline": False
                }),
                "repeats": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
            },
            "optional": {
                "filenames": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "prompts", "filenames")
    OUTPUT_IS_LIST = (True, True, True)
    FUNCTION = "generate_outfits"
    CATEGORY = "ExpressionNodes"

    def generate_outfits(self, images, outfit_name, repeats, filenames=None):
        batch_size = images.shape[0]

        out_images = []
        out_prompts = []
        out_filenames = []


        if filenames is None:
            filenames = ["image"] * batch_size
        elif isinstance(filenames, str):
            filenames = [filenames] * batch_size
        elif isinstance(filenames, list):
            if len(filenames) != batch_size:
                filenames = [f"image_{i}" for i in range(batch_size)]

        for i in range(batch_size):
            img = images[i]
            fname = filenames[i]

            if "." in fname:
                fname = fname.rsplit(".", 1)[0]

            prompt = f"changing outfit to {outfit_name}"

            for r in range(repeats):
                out_images.append(img.unsqueeze(0))
                out_prompts.append(prompt)
                out_filenames.append(f"{fname}_{outfit_name}_{r+1}")

        return (out_images, out_prompts, out_filenames)

class OutfitGeneratorExpressions:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        expressions = EXPRESSIONS

        inputs = {
            "required": {
                "prompt": ("STRING", {
                    "default": "changing outfit to Red Dress",
                    "multiline": True
                }),
                "repeats": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
            },
            "optional": {}
        }

        for expr in expressions:
            inputs["optional"][expr] = ("IMAGE",)

        return inputs

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "prompts", "filenames")
    OUTPUT_IS_LIST = (True, True, True)
    FUNCTION = "generate_outfits_expressions"
    CATEGORY = "ExpressionNodes"

    def generate_outfits_expressions(self, prompt, repeats, **kwargs):
        out_images = []
        out_prompts = []
        out_filenames = []

        expressions = EXPRESSIONS

        for expr in expressions:
            if expr in kwargs and kwargs[expr] is not None:
                images = kwargs[expr]

                batch_size = images.shape[0]

                for i in range(batch_size):
                    img = images[i]

                    base_name = expr

                    for r in range(repeats):
                        out_images.append(img.unsqueeze(0))
                        out_prompts.append(prompt)
                        out_filenames.append(base_name)

        if not out_images:
            pass

        return (out_images, out_prompts, out_filenames)

NODE_CLASS_MAPPINGS = {
    "SpritePromptGenerator": SpritePromptGenerator,
    "ExpressionGenerator": ExpressionGenerator,
    "OutfitGenerator": OutfitGenerator,
    "OutfitGeneratorExpressions": OutfitGeneratorExpressions
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SpritePromptGenerator": "Sprite Prompt Generator",
    "ExpressionGenerator": "Expression Generator (28)",
    "OutfitGenerator": "Outfit Generator (Batch)",
    "OutfitGeneratorExpressions": "Outfit Generator (Expressions, 28 Inputs)"
}
