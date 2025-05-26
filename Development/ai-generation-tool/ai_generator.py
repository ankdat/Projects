#!/usr/bin/env python3
"""
AI Generation Tool - A comprehensive Python script for AI-powered content generation
Supports 3D image generation, text-to-image generation, and text-to-video creation
"""

import os
import sys
import argparse
import logging
import json
import subprocess
import time
import uuid
import requests
from typing import Optional, Union, List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_generator')

class AIGenerator:
    """Main class for AI generation functionalities"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AI Generator with optional configuration
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.dependencies_checked = False
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration
        """
        default_config = {
            "triposr_model": "stabilityai/TripoSR",
            "stable_diffusion_model": "stabilityai/stable-diffusion-2-1",
            "output_dir": "output",
            "temp_dir": "temp",
            "api_keys": {
                "openai": os.environ.get("OPENAI_API_KEY", ""),
                "pexels": os.environ.get("PEXELS_API_KEY", "")
            },
            "video": {
                "duration": 30,
                "fps": 30,
                "resolution": [1920, 1080],
                "segment_duration": 3
            },
            "tts": {
                "provider": "edge",  # "edge" or "elevenlabs"
                "voice": "en-US-AriaNeural"  # Default voice for EdgeTTS
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge configs, with user config taking precedence
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                
        # Create output and temp directories if they don't exist
        os.makedirs(default_config["output_dir"], exist_ok=True)
        os.makedirs(default_config["temp_dir"], exist_ok=True)
        
        return default_config
    
    def check_dependencies(self, force_check: bool = False) -> bool:
        """
        Check if all required dependencies are installed
        
        Args:
            force_check: Force dependency check even if already performed
            
        Returns:
            True if all dependencies are installed, False otherwise
        """
        if self.dependencies_checked and not force_check:
            return True
            
        logger.info("Checking dependencies...")
        
        # List of required packages for each functionality
        requirements = {
            "3d_image": ["torch", "PIL", "numpy", "tsr"],
            "text_to_image": ["torch", "diffusers", "transformers", "PIL", "accelerate", "scipy", "safetensors"],
            "text_to_video": ["openai", "edge-tts", "whisper", "requests", "moviepy"]
        }
        
        missing_packages = []
        
        # Check each package
        for category, packages in requirements.items():
            for package in packages:
                try:
                    if package == "PIL":
                        __import__("PIL")
                    else:
                        __import__(package)
                except ImportError:
                    missing_packages.append(package)
        
        if missing_packages:
            logger.warning(f"Missing dependencies: {', '.join(missing_packages)}")
            logger.info("Installing missing dependencies...")
            
            # Try to install missing packages
            for package in missing_packages:
                # Special case for tsr which needs to be cloned from GitHub
                if package == "tsr":
                    logger.info("TripoSR needs to be installed from GitHub...")
                    if not os.path.exists("TripoSR"):
                        subprocess.run(["git", "clone", "https://github.com/pyimagesearch/TripoSR.git"], check=True)
                        subprocess.run(["pip", "install", "-r", "TripoSR/requirements.txt"], check=True)
                        # Add to Python path
                        sys.path.append(os.path.abspath("TripoSR"))
                        sys.path.append(os.path.abspath("TripoSR/tsr"))
                else:
                    subprocess.run(["pip", "install", package], check=True)
            
            # Verify installation
            for package in missing_packages:
                try:
                    if package == "PIL":
                        __import__("PIL")
                    elif package == "tsr":
                        # Skip direct import check for tsr as it's added to path
                        pass
                    else:
                        __import__(package)
                except ImportError:
                    logger.error(f"Failed to install {package}")
                    return False
        
        self.dependencies_checked = True
        logger.info("All dependencies are installed")
        return True

    def generate_3d_image(self, 
                         input_image_path: str, 
                         output_path: Optional[str] = None,
                         remove_background: bool = True,
                         output_format: str = "obj") -> str:
        """
        Generate a 3D model from a 2D image using TripoSR
        
        Args:
            input_image_path: Path to input image
            output_path: Path to save the output 3D model (optional)
            remove_background: Whether to remove background from input image
            output_format: Output format ('obj' or 'stl')
            
        Returns:
            Path to the generated 3D model
        """
        if not self.check_dependencies():
            raise RuntimeError("Dependencies check failed")
            
        if not os.path.exists(input_image_path):
            raise FileNotFoundError(f"Input image not found: {input_image_path}")
            
        # Import required modules
        try:
            import torch
            from PIL import Image
            import numpy as np
            # Add TripoSR to path if not already
            if "TripoSR" not in sys.path:
                if os.path.exists("TripoSR"):
                    sys.path.append(os.path.abspath("TripoSR"))
                    sys.path.append(os.path.abspath("TripoSR/tsr"))
            
            # Import TripoSR modules
            from tsr.system import TSR
            from tsr.utils import remove_background as rb, resize_foreground
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            raise
            
        # Set default output path if not provided
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(input_image_path))[0]
            output_path = os.path.join(self.config["output_dir"], f"{base_name}_3d.{output_format}")
            
        # Prepare output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        logger.info(f"Generating 3D model from {input_image_path}")
        
        # Process the image
        try:
            # Load image
            image = Image.open(input_image_path)
            
            # Resize image if needed (TripoSR works best with 512x512)
            if max(image.size) > 512:
                logger.info("Resizing image to fit within 512x512")
                image.thumbnail((512, 512))
                
            # Remove background if requested
            if remove_background:
                logger.info("Removing background from image")
                image = rb(image)
                
            # Save processed image temporarily
            temp_image_path = os.path.join(self.config["temp_dir"], "processed_input.png")
            image.save(temp_image_path)
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Initialize TripoSR model
            logger.info("Initializing TripoSR model")
            model = TSR.from_pretrained(
                self.config["triposr_model"],
                config_name="config.yaml",
                weight_name="model.ckpt",
                device=device
            )
            
            # Process the image with TripoSR
            logger.info("Processing image with TripoSR")
            mesh = model.process_image(temp_image_path, device=device)
            
            # Save the mesh
            logger.info(f"Saving 3D model to {output_path}")
            model.save_mesh(mesh, output_path)
            
            logger.info("3D model generation completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating 3D model: {e}")
            raise
    
    def generate_image_from_text(self,
                               prompt: str,
                               output_path: Optional[str] = None,
                               width: int = 512,
                               height: int = 512,
                               num_inference_steps: int = 50,
                               guidance_scale: float = 7.5,
                               negative_prompt: Optional[str] = None) -> str:
        """
        Generate an image from text description using Stable Diffusion
        
        Args:
            prompt: Text description for image generation
            output_path: Path to save the output image (optional)
            width: Width of the generated image
            height: Height of the generated image
            num_inference_steps: Number of denoising steps (higher = better quality but slower)
            guidance_scale: Scale for classifier-free guidance (higher = more adherence to prompt)
            negative_prompt: Text description of what to avoid in the image (optional)
            
        Returns:
            Path to the generated image
        """
        if not self.check_dependencies():
            raise RuntimeError("Dependencies check failed")
            
        # Import required modules
        try:
            import torch
            from diffusers import StableDiffusionPipeline
            from PIL import Image
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            raise
            
        # Set default output path if not provided
        if output_path is None:
            # Create a safe filename from the prompt
            safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            output_path = os.path.join(self.config["output_dir"], f"{safe_prompt}.png")
            
        # Prepare output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        logger.info(f"Generating image from text: '{prompt}'")
        
        try:
            # Determine device and dtype
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            logger.info(f"Using device: {device} with dtype: {dtype}")
            
            # Initialize Stable Diffusion pipeline
            logger.info("Initializing Stable Diffusion model")
            pipeline = StableDiffusionPipeline.from_pretrained(
                self.config["stable_diffusion_model"],
                torch_dtype=dtype
            )
            pipeline = pipeline.to(device)
            
            # Optional memory optimization
            if device == "cuda":
                pipeline.enable_attention_slicing()
            
            # Generate the image
            logger.info("Generating image")
            generation_args = {
                "prompt": prompt,
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
            }
            
            if negative_prompt:
                generation_args["negative_prompt"] = negative_prompt
                
            result = pipeline(**generation_args)
            
            # Save the image
            image = result.images[0]
            logger.info(f"Saving image to {output_path}")
            image.save(output_path)
            
            logger.info("Image generation completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating image from text: {e}")
            raise
    
    def generate_video_from_text(self,
                               prompt: str,
                               output_path: Optional[str] = None,
                               duration: Optional[int] = None,
                               resolution: Optional[Tuple[int, int]] = None,
                               voice: Optional[str] = None) -> str:
        """
        Generate a video from text description using Text-To-Video-AI workflow
        
        Args:
            prompt: Text description or topic for video generation
            output_path: Path to save the output video (optional)
            duration: Duration of the video in seconds (optional)
            resolution: Resolution of the video as (width, height) (optional)
            voice: Voice to use for text-to-speech (optional)
            
        Returns:
            Path to the generated video
        """
        if not self.check_dependencies():
            raise RuntimeError("Dependencies check failed")
            
        # Check API keys
        if not self.config["api_keys"]["openai"]:
            raise ValueError("OpenAI API key is required for text-to-video generation")
        if not self.config["api_keys"]["pexels"]:
            raise ValueError("Pexels API key is required for text-to-video generation")
            
        # Import required modules
        try:
            import openai
            import edge_tts
            import whisper
            import moviepy.editor as mp
            from moviepy.editor import TextClip, CompositeVideoClip
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            raise
            
        # Set default output path if not provided
        if output_path is None:
            # Create a safe filename from the prompt
            safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            output_path = os.path.join(self.config["output_dir"], f"{safe_prompt}.mp4")
            
        # Use default values from config if not provided
        if duration is None:
            duration = self.config["video"]["duration"]
        if resolution is None:
            resolution = tuple(self.config["video"]["resolution"])
        if voice is None:
            voice = self.config["tts"]["voice"]
            
        # Prepare output directory and temp directory for intermediate files
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        temp_dir = os.path.join(self.config["temp_dir"], f"video_{uuid.uuid4().hex}")
        os.makedirs(temp_dir, exist_ok=True)
            
        logger.info(f"Generating video from text: '{prompt}'")
        
        try:
            # Step 1: Generate script from topic using OpenAI
            logger.info("Generating script from topic")
            script = self._generate_script(prompt, duration)
            script_path = os.path.join(temp_dir, "script.txt")
            with open(script_path, 'w') as f:
                f.write(script)
            logger.info(f"Script generated and saved to {script_path}")
            
            # Step 2: Generate audio from script using EdgeTTS
            logger.info(f"Generating audio from script using voice: {voice}")
            audio_path = os.path.join(temp_dir, "audio.mp3")
            self._generate_audio(script, audio_path, voice)
            logger.info(f"Audio generated and saved to {audio_path}")
            
            # Step 3: Generate timed captions from audio using Whisper
            logger.info("Generating timed captions from audio")
            captions = self._generate_captions(audio_path)
            captions_path = os.path.join(temp_dir, "captions.json")
            with open(captions_path, 'w') as f:
                json.dump(captions, f, indent=2)
            logger.info(f"Captions generated and saved to {captions_path}")
            
            # Step 4: Generate visual keywords for each caption segment
            logger.info("Generating visual keywords for captions")
            visual_keywords = self._generate_visual_keywords(captions)
            keywords_path = os.path.join(temp_dir, "keywords.json")
            with open(keywords_path, 'w') as f:
                json.dump(visual_keywords, f, indent=2)
            logger.info(f"Visual keywords generated and saved to {keywords_path}")
            
            # Step 5: Fetch videos for each keyword from Pexels
            logger.info("Fetching videos for keywords from Pexels")
            video_segments = self._fetch_videos(visual_keywords, temp_dir)
            segments_path = os.path.join(temp_dir, "segments.json")
            with open(segments_path, 'w') as f:
                json.dump(video_segments, f, indent=2)
            logger.info(f"Video segments fetched and saved to {segments_path}")
            
            # Step 6: Stitch together videos, audio, and captions
            logger.info("Stitching together videos, audio, and captions")
            self._create_final_video(video_segments, audio_path, captions, output_path, resolution)
            logger.info(f"Final video created and saved to {output_path}")
            
            logger.info("Video generation completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating video from text: {e}")
            raise
            
    def _generate_script(self, topic: str, duration: int) -> str:
        """
        Generate a video script from a topic using OpenAI
        
        Args:
            topic: Topic for the video
            duration: Target duration in seconds
            
        Returns:
            Generated script
        """
        # Set up OpenAI client
        from openai import OpenAI
        client = OpenAI(api_key=self.config["api_keys"]["openai"])
        
        # Calculate approximate word count based on duration (assuming ~150 words per minute)
        word_count = int((duration / 60) * 150)
        
        # Create prompt for script generation
        prompt = f"""You are a seasoned content writer for a video channel, specializing in informative videos.
        Your videos are concise, lasting about {duration} seconds (approximately {word_count} words).
        They are engaging, informative, and original.
        
        Create a script about: {topic}
        
        The script should be well-structured with a clear introduction, body, and conclusion.
        Keep it interesting and suitable for a general audience.
        Aim for approximately {word_count} words.
        """
        
        # Generate script using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
        
        script = response.choices[0].message.content
        return script
    
    def _generate_audio(self, script: str, output_path: str, voice: str) -> None:
        """
        Generate audio from script using EdgeTTS
        
        Args:
            script: Script to convert to speech
            output_path: Path to save the audio file
            voice: Voice to use for text-to-speech
        """
        import asyncio
        import edge_tts
        
        async def _generate():
            communicate = edge_tts.Communicate(script, voice)
            await communicate.save(output_path)
            
        # Run the async function
        asyncio.run(_generate())
    
    def _generate_captions(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Generate timed captions from audio using Whisper
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of caption segments with timing information
        """
        import whisper
        
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe audio
        result = model.transcribe(audio_path, word_timestamps=True)
        
        # Process segments
        captions = []
        for segment in result["segments"]:
            captions.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })
            
        return captions
    
    def _generate_visual_keywords(self, captions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate visual keywords for each caption segment
        
        Args:
            captions: List of caption segments
            
        Returns:
            List of visual keywords for each segment
        """
        from openai import OpenAI
        client = OpenAI(api_key=self.config["api_keys"]["openai"])
        
        # Combine captions into a single text for context
        full_text = " ".join([caption["text"] for caption in captions])
        
        # Process captions in segments of 3 seconds
        segment_duration = self.config["video"]["segment_duration"]
        visual_keywords = []
        
        # Create segments based on caption timing
        current_time = 0
        end_time = captions[-1]["end"]
        
        while current_time < end_time:
            segment_end = min(current_time + segment_duration, end_time)
            
            # Find captions that overlap with this segment
            segment_captions = [
                caption["text"] for caption in captions 
                if (caption["start"] < segment_end and caption["end"] > current_time)
            ]
            
            if segment_captions:
                segment_text = " ".join(segment_captions)
                
                # Generate keywords using OpenAI
                prompt = f"""Given the following video script segment, extract three visually concrete and specific keywords 
                that can be used to search for background videos. The keywords should be short (1-2 words) and capture 
                the main visual essence of the text.

                Script segment: "{segment_text}"

                Context of full script: "{full_text[:500]}..."

                Return only the three keywords as a comma-separated list. Each keyword should be visually concrete 
                and suitable for video search.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You extract visual keywords from text for video creation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50
                )
                
                # Parse keywords
                keywords_text = response.choices[0].message.content.strip()
                keywords = [k.strip() for k in keywords_text.split(",")][:3]
                
                visual_keywords.append({
                    "start": current_time,
                    "end": segment_end,
                    "text": segment_text,
                    "keywords": keywords
                })
            
            current_time = segment_end
            
        return visual_keywords
    
    def _fetch_videos(self, visual_keywords: List[Dict[str, Any]], temp_dir: str) -> List[Dict[str, Any]]:
        """
        Fetch videos for each keyword from Pexels
        
        Args:
            visual_keywords: List of visual keywords for each segment
            temp_dir: Directory to save downloaded videos
            
        Returns:
            List of video segments with paths to downloaded videos
        """
        import requests
        
        # Create directory for video segments
        segments_dir = os.path.join(temp_dir, "segments")
        os.makedirs(segments_dir, exist_ok=True)
        
        video_segments = []
        
        for i, segment in enumerate(visual_keywords):
            segment_path = None
            
            # Try each keyword until we find a suitable video
            for keyword in segment["keywords"]:
                if segment_path:
                    break
                    
                # Search for videos on Pexels
                url = "https://api.pexels.com/videos/search"
                headers = {
                    "Authorization": self.config["api_keys"]["pexels"]
                }
                params = {
                    "query": keyword,
                    "orientation": "landscape",
                    "per_page": 15,
                    "size": "large"
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["videos"]:
                        # Find a suitable video
                        for video in data["videos"]:
                            # Get the highest quality video file
                            video_files = sorted(
                                video["video_files"], 
                                key=lambda x: x.get("width", 0) * x.get("height", 0),
                                reverse=True
                            )
                            
                            if video_files:
                                video_url = video_files[0]["link"]
                                segment_path = os.path.join(segments_dir, f"segment_{i:03d}.mp4")
                                
                                # Download the video
                                with requests.get(video_url, stream=True) as r:
                                    r.raise_for_status()
                                    with open(segment_path, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                
                                logger.info(f"Downloaded video for keyword '{keyword}' to {segment_path}")
                                break
            
            # If no video found, use a placeholder
            if not segment_path:
                logger.warning(f"No video found for segment {i}, using placeholder")
                # Create a placeholder video using MoviePy
                import moviepy.editor as mp
                
                segment_path = os.path.join(segments_dir, f"segment_{i:03d}.mp4")
                duration = segment["end"] - segment["start"]
                
                # Create a simple colored clip with text
                clip = mp.ColorClip(
                    size=(1920, 1080),
                    color=(0, 0, 0),
                    duration=duration
                )
                
                # Add text
                text_clip = mp.TextClip(
                    segment["text"],
                    fontsize=48,
                    color='white',
                    size=(1800, 900),
                    method='caption',
                    align='center'
                ).set_duration(duration)
                
                # Composite
                final_clip = mp.CompositeVideoClip([clip, text_clip.set_position('center')])
                final_clip.write_videofile(segment_path, fps=30, codec='libx264')
            
            # Add to segments list
            video_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "path": segment_path,
                "text": segment["text"]
            })
        
        return video_segments
    
    def _create_final_video(self, 
                          video_segments: List[Dict[str, Any]], 
                          audio_path: str, 
                          captions: List[Dict[str, Any]], 
                          output_path: str,
                          resolution: Tuple[int, int]) -> None:
        """
        Create the final video by stitching together video segments, audio, and captions
        
        Args:
            video_segments: List of video segments with paths
            audio_path: Path to the audio file
            captions: List of caption segments
            output_path: Path to save the final video
            resolution: Resolution of the final video as (width, height)
        """
        import moviepy.editor as mp
        from moviepy.editor import TextClip, CompositeVideoClip
        
        # Load audio
        audio = mp.AudioFileClip(audio_path)
        
        # Process video segments
        clips = []
        
        for segment in video_segments:
            # Load video clip
            video_clip = mp.VideoFileClip(segment["path"])
            
            # Trim or loop to match segment duration
            segment_duration = segment["end"] - segment["start"]
            
            if video_clip.duration < segment_duration:
                # Loop the clip
                video_clip = video_clip.loop(duration=segment_duration)
            else:
                # Trim the clip
                video_clip = video_clip.subclip(0, segment_duration)
            
            # Resize to match resolution
            video_clip = video_clip.resize(width=resolution[0], height=resolution[1])
            
            # Set start time
            video_clip = video_clip.set_start(segment["start"])
            
            clips.append(video_clip)
        
        # Create caption clips
        for caption in captions:
            caption_duration = caption["end"] - caption["start"]
            
            # Create text clip
            text_clip = TextClip(
                caption["text"],
                fontsize=36,
                color='white',
                bg_color='black',
                size=(resolution[0] - 100, None),
                method='caption',
                align='center'
            ).set_duration(caption_duration)
            
            # Add stroke to text for better visibility
            text_clip = text_clip.margin(opacity=0)
            
            # Position at the bottom
            text_clip = text_clip.set_position(('center', 'bottom')).margin(bottom=50)
            
            # Set start time
            text_clip = text_clip.set_start(caption["start"])
            
            clips.append(text_clip)
        
        # Combine all clips
        final_clip = CompositeVideoClip(clips, size=resolution)
        
        # Add audio
        final_clip = final_clip.set_audio(audio)
        
        # Write final video
        final_clip.write_videofile(
            output_path,
            fps=self.config["video"]["fps"],
            codec='libx264',
            audio_codec='aac'
        )
            
    def _setup_3d_generation(self) -> None:
        """
        Setup environment for 3D image generation
        """
        logger.info("Setting up environment for 3D image generation")
        
        # Check if TripoSR is already cloned
        if not os.path.exists("TripoSR"):
            logger.info("Cloning TripoSR repository")
            subprocess.run(["git", "clone", "https://github.com/pyimagesearch/TripoSR.git"], check=True)
            
            # Install requirements
            logger.info("Installing TripoSR requirements")
            subprocess.run(["pip", "install", "-r", "TripoSR/requirements.txt"], check=True)
            
        # Add to Python path
        sys.path.append(os.path.abspath("TripoSR"))
        sys.path.append(os.path.abspath("TripoSR/tsr"))
        
        logger.info("3D image generation environment setup completed")
        
    def _setup_text_to_image_generation(self) -> None:
        """
        Setup environment for text-to-image generation
        """
        logger.info("Setting up environment for text-to-image generation")
        
        # Check and install required packages
        required_packages = ["diffusers", "transformers", "accelerate", "scipy", "safetensors"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.run(["pip", "install"] + missing_packages, check=True)
            
        logger.info("Text-to-image generation environment setup completed")
        
    def _setup_text_to_video_generation(self) -> None:
        """
        Setup environment for text-to-video generation
        """
        logger.info("Setting up environment for text-to-video generation")
        
        # Check and install required packages
        required_packages = ["openai", "edge-tts", "whisper", "moviepy"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.run(["pip", "install"] + missing_packages, check=True)
            
        logger.info("Text-to-video generation environment setup completed")


def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="AI Generation Tool")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 3D image generation command
    parser_3d = subparsers.add_parser("3d", help="Generate 3D model from image")
    parser_3d.add_argument("input", help="Path to input image")
    parser_3d.add_argument("--output", "-o", help="Path to output 3D model")
    parser_3d.add_argument("--keep-background", action="store_true", help="Keep image background")
    parser_3d.add_argument("--format", choices=["obj", "stl"], default="obj", help="Output format (obj or stl)")
    
    # Text to image command
    parser_t2i = subparsers.add_parser("text2img", help="Generate image from text")
    parser_t2i.add_argument("prompt", help="Text prompt for image generation")
    parser_t2i.add_argument("--output", "-o", help="Path to output image")
    parser_t2i.add_argument("--width", type=int, default=512, help="Width of the generated image")
    parser_t2i.add_argument("--height", type=int, default=512, help="Height of the generated image")
    parser_t2i.add_argument("--steps", type=int, default=50, help="Number of inference steps")
    parser_t2i.add_argument("--guidance", type=float, default=7.5, help="Guidance scale")
    parser_t2i.add_argument("--negative-prompt", help="Negative prompt (what to avoid in the image)")
    
    # Text to video command
    parser_t2v = subparsers.add_parser("text2video", help="Generate video from text")
    parser_t2v.add_argument("prompt", help="Text prompt for video generation")
    parser_t2v.add_argument("--output", "-o", help="Path to output video")
    parser_t2v.add_argument("--duration", type=int, help="Duration of the video in seconds")
    parser_t2v.add_argument("--width", type=int, help="Width of the video")
    parser_t2v.add_argument("--height", type=int, help="Height of the video")
    parser_t2v.add_argument("--voice", help="Voice to use for text-to-speech")
    
    # General options
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = AIGenerator(args.config)
    
    # Execute command
    if args.command == "3d":
        output_path = generator.generate_3d_image(
            args.input,
            args.output,
            not args.keep_background,
            args.format
        )
        print(f"3D model generated successfully: {output_path}")
    elif args.command == "text2img":
        output_path = generator.generate_image_from_text(
            args.prompt,
            args.output,
            args.width,
            args.height,
            args.steps,
            args.guidance,
            args.negative_prompt
        )
        print(f"Image generated successfully: {output_path}")
    elif args.command == "text2video":
        # Parse resolution if provided
        resolution = None
        if args.width and args.height:
            resolution = (args.width, args.height)
            
        output_path = generator.generate_video_from_text(
            args.prompt,
            args.output,
            args.duration,
            resolution,
            args.voice
        )
        print(f"Video generated successfully: {output_path}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
