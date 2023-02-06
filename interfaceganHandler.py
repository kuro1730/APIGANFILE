import os

import dlib
import numpy as np
import torch

from models.model_settings import MODEL_POOL
from models.pggan_generator import PGGANGenerator
from models.stylegan_generator import StyleGANGenerator
from latent_encoder.models.latent_optimizer import LatentOptimizer
from latent_encoder.models.losses import LatentLoss
from latent_encoder.utilities.hooks import GeneratedImageHook
from latent_encoder.utilities.images import load_images
from tqdm import tqdm


class itfgan_webObject:

    def __init__(self):
        self.model = {
            'stylegan_ffhq': None,
            'stylegan_celebahq': None,
            'pggan_celebahq': None
        }
        self.synthesizer = None

    def build_generatorS(self):
        self.cleanCache()
        self.model['stylegan_ffhq']     = StyleGANGenerator('stylegan_ffhq')
        self.model['stylegan_celebahq'] = StyleGANGenerator('stylegan_celebahq')
        self.synthesizer = StyleGANGenerator("stylegan_ffhq").model.synthesis

    def build_generatorP(self):
        self.cleanCache()
        self.model['pggan_celebahq'] = PGGANGenerator('pggan_celebahq')
    
    def cleanCache(self):
        torch.cuda.empty_cache()

    def randomSamplig(self, model_name, latentSpaceType, num):
        self.cleanCache()
        for name in self.model:
            if model_name is name: generator = self.model[name] 

        if latentSpaceType == 'W': kwargs = {'latent_space_type': 'W'}
        else: kwargs = {}
        codes = generator.easy_sample(num)
        if latentSpaceType == 'W':
              codes = torch.from_numpy(codes).type(torch.FloatTensor).to(generator.run_device)
              codes = generator.get_value(generator.model.mapping(codes))

        origin_image = generator.easy_synthesize(codes, **kwargs)['image']

        return codes, origin_image


    def manipulate(self, 
        latentCode, model_name, latentSpaceType,ATTRS,boundaries,
        age, eyeglasses, gender, pose, smile, 
        check_if_upload = True
    ):
      self.cleanCache()    
      for name in self.model:
          if model_name is name: model = self.model[name]

      if latentSpaceType == 'W': kwargs = {'latent_space_type': 'W'}
      else: kwargs = {}

      if check_if_upload is True: kwargs = {'latent_space_type': 'WP'}

      latentCode = model.preprocess(latentCode, **kwargs)

      
      new_codes = latentCode.copy()
      for attr_name in ATTRS:
          new_codes += boundaries[attr_name] * eval(attr_name)
      
      newImage = model.easy_synthesize(new_codes, **kwargs)['image']
      return newImage

    def optimize_latents(self, input_image, optimize_iterations):


            if input_image is None: return
            latent_optimizer = LatentOptimizer(self.synthesizer, 12)

            for param in latent_optimizer.parameters():
                param.requires_grad_(False)

            
            reference_image = load_images([input_image])
            reference_image = torch.from_numpy(reference_image).cuda()
            reference_image = latent_optimizer.vgg_processing(reference_image)
            reference_features = latent_optimizer.vgg16(reference_image).detach()
            reference_image = reference_image.detach()
            latents_to_be_optimized = torch.zeros((1,18,512)).cuda().requires_grad_(True)
            
            criterion = LatentLoss()
            optimizer = torch.optim.SGD([latents_to_be_optimized], lr=1)
            
            progress_bar = tqdm(range(optimize_iterations))
            for step in progress_bar:
 
                
                optimizer.zero_grad()
                generated_image_features = latent_optimizer(latents_to_be_optimized)
                loss = criterion(generated_image_features, reference_features)
                loss.backward()
                loss = loss.item()

                optimizer.step()
                progress_bar.set_description("Step: {}, Loss: {}".format(step, loss))
                    

            optimized_dlatents = latents_to_be_optimized.detach().cpu().numpy()
            return optimized_dlatents
