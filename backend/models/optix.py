import torch
import torch.nn as nn
from backend.models.neurix import NeurixTransformer
from backend.models.config import ModelConfig, get_config

class VisionProjectionEncoder(nn.Module):
    def __init__(self, in_channels: int = 3, image_size: int = 224, patch_size: int = 16, embed_dim: int = 768):
        super().__init__()
        self.patch_embed = nn.Conv2d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        num_patches = (image_size // patch_size) ** 2
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))

    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        # pixel_values: [B, C, H, W] -> [B, Embed, PatchesH, PatchesW]
        x = self.patch_embed(pixel_values).flatten(2).transpose(1, 2)
        return x + self.pos_embed

class OptixModel(nn.Module):
    """
    Optix Model: Multimodal Vision + Language Transformer with decoupled image encoder projection
    and causal language decoder.
    STATUS: EXPERIMENTAL — NOT TRAINED
    """
    def __init__(self, config: ModelConfig = None):
        super().__init__()
        if config is None:
            config = get_config("optix")
        self.config = config
        self.vision_encoder = VisionProjectionEncoder(embed_dim=config.d_model)
        self.decoder = NeurixTransformer(config)

    def forward(self, input_ids: torch.Tensor, pixel_values: torch.Tensor = None):
        if pixel_values is not None:
            vision_tokens = self.vision_encoder(pixel_values)
            text_tokens = self.decoder.tok_embeddings(input_ids)
            combined = torch.cat([vision_tokens, text_tokens], dim=1)
            for layer in self.decoder.layers:
                combined = layer(combined)
            return self.decoder.lm_head(self.decoder.norm(combined))
        return self.decoder(input_ids)

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

def build_optix_model() -> OptixModel:
    return OptixModel()
