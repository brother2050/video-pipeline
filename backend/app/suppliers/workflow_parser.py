"""
ComfyUI Workflow Parser.
Automatically analyzes workflow JSON structure, locates key nodes, supports parameter overrides.
Compatible with any custom workflow, no hardcoded node IDs required.
"""

import copy
import random
from typing import Any, Optional


class WorkflowParser:
    """ComfyUI workflow auto-analysis and parameter injection."""

    IMAGE_REF_KEYS: set[str] = {
        "start_image", "end_image", "image", "image1", "image2", "image3",
        "input_image", "reference_image", "first_frame", "last_frame",
        "start_frame", "end_frame", "init_image", "img", "img1", "img2",
    }

    FRAME_KEYS: tuple[str, ...] = ("video_frames", "length", "frames", "num_frames")

    def __init__(self, workflow: dict[str, Any]) -> None:
        self.workflow = workflow
        self._analysis: Optional[dict[str, Any]] = None

    def analyze(self) -> dict[str, Any]:
        """Analyze workflow structure, cache results."""
        if self._analysis is not None:
            return self._analysis

        a: dict[str, Any] = {
            "text_nodes": [],
            "sampler_nodes": [],
            "latent_nodes": [],
            "video_latent_nodes": [],
            "checkpoint_nodes": [],
            "save_nodes": [],
            "load_image_nodes": [],
            "image_slot_map": {},
            "positive_text_nodes": [],
            "negative_text_nodes": [],
            "unlinked_text_nodes": [],
            "frame_key_found": {},
            "all_node_ids": [],
        }

        for nid, node in self.workflow.items():
            if not isinstance(node, dict):
                continue
            ct = node.get("class_type", "")
            inp = node.get("inputs", {})
            if not isinstance(inp, dict):
                continue

            a["all_node_ids"].append(nid)
            entry: dict[str, Any] = {"id": nid, "class_type": ct, "inputs": inp}

            if "text" in inp:
                a["text_nodes"].append(entry)
            if "positive" in inp and "negative" in inp:
                a["sampler_nodes"].append(entry)
            if "width" in inp and "height" in inp:
                a["latent_nodes"].append(entry)
                for fk in self.FRAME_KEYS:
                    if fk in inp:
                        a["video_latent_nodes"].append(entry)
                        a["frame_key_found"][nid] = fk
                        break
            if "ckpt_name" in inp or "unet_name" in inp:
                a["checkpoint_nodes"].append(entry)
            if "Save" in ct or "save" in ct:
                a["save_nodes"].append(entry)
            if "LoadImage" in ct or "load_image" in ct.lower():
                a["load_image_nodes"].append(entry)

        # Distinguish positive / negative prompt nodes
        pos_ids: set[str] = set()
        neg_ids: set[str] = set()
        for s in a["sampler_nodes"]:
            for ref_field, id_set in [("positive", pos_ids), ("negative", neg_ids)]:
                t = self._resolve_ref(s["inputs"].get(ref_field))
                if t:
                    id_set.add(t)

        for t in a["text_nodes"]:
            if t["id"] in pos_ids:
                a["positive_text_nodes"].append(t)
            elif t["id"] in neg_ids:
                a["negative_text_nodes"].append(t)
            else:
                a["unlinked_text_nodes"].append(t)

        # Image slot tracking
        for nid, node in self.workflow.items():
            if not isinstance(node, dict):
                continue
            inp = node.get("inputs", {})
            if not isinstance(inp, dict):
                continue
            for key, val in inp.items():
                if key.lower() not in {k.lower() for k in self.IMAGE_REF_KEYS}:
                    continue
                target = self._resolve_ref(val)
                if not target:
                    continue
                target_node = self.workflow.get(target)
                if not target_node:
                    continue
                if target in a["image_slot_map"]:
                    a["image_slot_map"][target]["slots"][key] = nid
                else:
                    a["image_slot_map"][target] = {
                        "node_id": target,
                        "class_type": target_node.get("class_type", ""),
                        "slots": {key: nid},
                    }

        self._analysis = a
        return a

    @staticmethod
    def _resolve_ref(ref: Any) -> Optional[str]:
        """Resolve node reference ([node_id, slot_index] or string)."""
        if isinstance(ref, list) and len(ref) >= 1:
            return str(ref[0])
        if isinstance(ref, (str, int)):
            return str(ref)
        return None

    def apply_overrides(self, overrides: dict[str, Any]) -> dict[str, Any]:
        """
        Apply parameter overrides to a workflow copy.
        Automatically locates corresponding nodes and injects parameters.

        Supported override keys:
        - positive / negative: prompt text
        - width / height: image dimensions
        - frames: video frame count
        - batch_size: batch size
        - steps / cfg / sampler_name / scheduler / denoise: sampler params
        - seed: random seed (-1 for random)
        - checkpoint: model filename
        - lora_strength: LoRA strength
        - start_image / end_image / image / input_image / init_image
          / first_frame / last_frame / start_frame / end_frame
          / reference_image: input image filenames (uploaded to ComfyUI)
        """
        wf = copy.deepcopy(self.workflow)
        a = self.analyze()

        # Prompts
        for key, nlist in [
            ("positive", a["positive_text_nodes"]),
            ("negative", a["negative_text_nodes"]),
        ]:
            if key not in overrides:
                continue
            targets = nlist
            if not targets and key == "positive" and a["unlinked_text_nodes"]:
                targets = [a["unlinked_text_nodes"][0]]
            elif not targets and key == "negative" and len(a["unlinked_text_nodes"]) > 1:
                targets = [a["unlinked_text_nodes"][1]]
            for n in targets:
                if n["id"] in wf:
                    wf[n["id"]]["inputs"]["text"] = overrides[key]

        # Dimensions
        w, h = overrides.get("width"), overrides.get("height")
        for n in a["latent_nodes"]:
            nid = n["id"]
            if nid not in wf:
                continue
            if w is not None:
                wf[nid]["inputs"]["width"] = w
            if h is not None:
                wf[nid]["inputs"]["height"] = h

        # Frames (video)
        if "frames" in overrides:
            for n in a["video_latent_nodes"]:
                nid = n["id"]
                if nid not in wf:
                    continue
                fk = a["frame_key_found"].get(nid, "video_frames")
                wf[nid]["inputs"][fk] = overrides["frames"]

        # Batch size
        if "batch_size" in overrides:
            for n in a["latent_nodes"]:
                if n["id"] in wf:
                    wf[n["id"]]["inputs"]["batch_size"] = overrides["batch_size"]

        # Sampler params
        for n in a["sampler_nodes"]:
            nid = n["id"]
            if nid not in wf:
                continue
            inp = wf[nid]["inputs"]
            for ok in ("steps", "cfg", "sampler_name", "scheduler", "denoise"):
                if ok in overrides:
                    inp[ok] = overrides[ok]
            if "seed" in overrides:
                val = random.randint(0, 2**53 - 1) if overrides["seed"] == -1 else overrides["seed"]
                for sk in ("seed", "noise_seed"):
                    if sk in inp:
                        inp[sk] = val
                        break

        # Checkpoint model
        if "checkpoint" in overrides:
            for n in a["checkpoint_nodes"]:
                nid = n["id"]
                if nid not in wf:
                    continue
                inp = wf[nid]["inputs"]
                if "ckpt_name" in inp:
                    inp["ckpt_name"] = overrides["checkpoint"]
                elif "unet_name" in inp:
                    inp["unet_name"] = overrides["checkpoint"]

        # LoRA
        if "lora_strength" in overrides:
            for nid_str, node in self.workflow.items():
                ct = node.get("class_type", "")
                if "Lora" not in ct and "lora" not in ct:
                    continue
                if nid_str not in wf:
                    continue
                for lk in ("strength_model", "strength_clip"):
                    if lk in wf[nid_str]["inputs"]:
                        wf[nid_str]["inputs"][lk] = overrides["lora_strength"]

        # Input images
        image_slot_keys = [
            "start_image", "end_image", "image", "input_image", "init_image",
            "first_frame", "last_frame", "start_frame", "end_frame", "reference_image",
        ]
        for slot_key in image_slot_keys:
            if slot_key not in overrides:
                continue
            uploaded_name = overrides[slot_key]
            placed = False
            # Priority: locate via slot tracking
            for target_nid, info in a["image_slot_map"].items():
                for slot, source_nid in info["slots"].items():
                    if slot.lower() == slot_key.lower() or slot_key.lower() in slot.lower():
                        if target_nid in wf:
                            wf[target_nid]["inputs"]["image"] = uploaded_name
                            placed = True
            # Fallback: assign to unused LoadImage nodes in order
            if not placed:
                for li in a["load_image_nodes"]:
                    lid = li["id"]
                    if lid in wf:
                        current = wf[lid]["inputs"].get("image", "")
                        already = any(overrides.get(k) == current for k in image_slot_keys)
                        if not already:
                            wf[lid]["inputs"]["image"] = uploaded_name
                            placed = True
                            break

        return wf

    def get_node_info(self) -> dict[str, Any]:
        """Return analysis summary for frontend display."""
        a = self.analyze()
        return {
            "total_nodes": len(a["all_node_ids"]),
            "checkpoint_nodes": [
                {"id": n["id"], "model": n["inputs"].get("ckpt_name") or n["inputs"].get("unet_name", "?")}
                for n in a["checkpoint_nodes"]
            ],
            "positive_text_nodes": [
                {"id": n["id"], "preview": n["inputs"].get("text", "")[:80]}
                for n in a["positive_text_nodes"]
            ],
            "negative_text_nodes": [
                {"id": n["id"], "preview": n["inputs"].get("text", "")[:80]}
                for n in a["negative_text_nodes"]
            ],
            "latent_nodes": [
                {"id": n["id"], "width": n["inputs"].get("width"), "height": n["inputs"].get("height")}
                for n in a["latent_nodes"]
            ],
            "sampler_nodes": [
                {"id": n["id"], "steps": n["inputs"].get("steps"), "cfg": n["inputs"].get("cfg")}
                for n in a["sampler_nodes"]
            ],
            "load_image_nodes": [
                {"id": n["id"], "image": n["inputs"].get("image", "?")}
                for n in a["load_image_nodes"]
            ],
            "has_video_nodes": len(a["video_latent_nodes"]) > 0,
        }
