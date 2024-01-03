import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer
from libs.config import parse_args
from libs.get_model import get_model_with_config, get_dataset

device = torch.device('cuda:1')

def main():
    cfg = parse_args()
    datamodule = get_dataset(cfg)
    model = get_model_with_config(cfg, datamodule)
    model.load_state_dict(torch.load(cfg.MODEL.CHECKPOINT)['state_dict'])
    model = model.to(device)
    model.eval()

    text_encoder = AutoModel.from_pretrained('./deps/clip-vit-base-patch16').to(device)
    tokenizer = AutoTokenizer.from_pretrained('./deps/clip-vit-base-patch16')

    with torch.no_grad():
        text_inputs = tokenizer(
            ["a person walks like a duck."], 
            padding="max_length",
            truncation=True,
            max_length=tokenizer.model_max_length,
            return_tensors="pt"
        )
        text_input_ids = text_inputs.input_ids
        caption = text_encoder.get_text_features(
            text_input_ids.to(text_encoder.device)
        ).cpu().numpy()


    with torch.no_grad():
        smpls = model.sample({
            "text":[caption], 
            "length":[120]
        }).cpu()
        smpls = datamodule.recover_motion(smpls, local_only=False)
        np.save('./demos/samples/duck.npy', smpls.v[..., [0,2,1]].numpy())


if __name__ == "__main__":
    main()

