
import torch
from transformers import GPT2LMHeadModel
from src.data_generation import get_act_ds, get_train_tests

from src.constants import device, tokenizer
from src.inlp import inlp
from src.rlace import rlace
from src.dir_methods import (
    get_rlace,
    get_inlp,
    get_grad_descent,
    get_embed_she_he,
    get_unembed_she_he,
    get_confusion_grad,
    get_grad_she_he,
    get_random,
)

import fire
from pathlib import Path


def run(model_name: str, n: int = 1, layer_nb: int = None):
    model: torch.nn.Module = GPT2LMHeadModel.from_pretrained(model_name).to(device)
    for param in model.parameters():
        param.requires_grad = False

    methods = [
        get_random,
        get_embed_she_he,
        get_unembed_she_he,
        get_confusion_grad,
        get_grad_she_he,
        get_inlp,
        get_rlace,
        get_grad_descent,
    ]

    train_tests = get_train_tests()
    layer_nb_ = layer_nb or len(model.transformer.h) // 2
    module_name = f"transformer.h.{layer_nb_}"
    layer = model.get_submodule(module_name)
    layers = {module_name: layer}
    train_ds = get_act_ds(model, train_tests, layer)

    for i in range(n):
        print("round", i)
        for m in methods:
            print(m.__name__)
            d = m(train_ds, train_tests, model, layer, seed=i)

            file_name = f"L{layer_nb} - {m.__name__} - {i} - v0.pt" if layer_nb else f"{m.__name__} - {i} - v0.pt"
            path = Path(".") / "saved_dirs" / model_name / file_name

            torch.save(d, str(path))


if __name__ == "__main__":
    fire.Fire(run)