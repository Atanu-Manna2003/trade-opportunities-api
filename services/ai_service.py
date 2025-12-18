"""AI service for generating market analysis reports using Google Gemini API."""

import os
import asyncio
import google.generativeai as genai
from typing import List, Dict, Optional
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger()


class AIService:
    """Service for generating market analysis reports using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI service with Gemini API.
        
        Args:
            api_key: Google Gemini API key (if None, reads from env)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # First, try to list available models to find what's actually available
        available_model_names = []
        available_models_full = []
        try:
            models = genai.list_models()
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    # Keep both full name and clean name
                    model_name_clean = model.name.replace('models/', '')
                    available_model_names.append(model_name_clean)
                    available_models_full.append(model.name)
            logger.info(f"Available Gemini models (clean): {available_model_names}")
            logger.info(f"Available Gemini models (full): {available_models_full}")
        except Exception as e:
            logger.warning(f"Could not list available models: {str(e)}")
            available_model_names = []
            available_models_full = []
        
        # Use environment variable for model name, default to gemini-pro (most commonly available)
        # Strip "gemini/" prefix if present (REST API format vs Python SDK format)
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")
        original_model_name = model_name
        if model_name.startswith("gemini/"):
            model_name = model_name.replace("gemini/", "")
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        
        # Try to initialize the model
        model_initialized = False
        models_to_try = []
        
        # Build list of models to try
        if available_models_full:
            # If we have the full list, use those first (they're guaranteed to work)
            models_to_try = available_models_full[:5]  # Try first 5 available models
            # Also add the user's specified model if it's in the list
            if model_name in available_model_names:
                idx = available_model_names.index(model_name)
                if available_models_full[idx] not in models_to_try:
                    models_to_try.insert(0, available_models_full[idx])
        else:
            # If we can't list models, try common models with different formats
            models_to_try = [
                model_name,  # User's specified model
                f"models/{model_name}",  # With models/ prefix
                "gemini-pro",
                "models/gemini-pro",
                "gemini-1.5-pro",
                "models/gemini-1.5-pro",
            ]
        
        last_error = None
        for try_model in models_to_try:
            try:
                # Try with the exact name from list_models first
                self.model = genai.GenerativeModel(try_model)
                logger.info(f"AI service initialized with Gemini API (model: {try_model})")
                model_initialized = True
                self.model_name_used = try_model
                break
            except Exception as e:
                last_error = e
                logger.debug(f"Failed to initialize model '{try_model}': {str(e)}")
                continue
        
        if not model_initialized:
            error_msg = f"Could not initialize any Gemini model. Tried: {models_to_try}. Last error: {str(last_error)}"
            if available_model_names:
                error_msg += f" Available models: {available_model_names}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    async def generate_market_report(
        self, sector: str, market_data: List[Dict[str, str]]
    ) -> str:
        """
        Generate a structured Markdown market analysis report.
        
        Args:
            sector: Sector name to analyze
            market_data: List of market data and news snippets
            
        Returns:
            Structured Markdown report string
        """
        try:
            # Build context from market data
            context = self._build_context(sector, market_data)
            
            # Create prompt for Gemini
            prompt = self._create_prompt(sector, context)
            
            logger.info(f"Generating market report for sector: {sector}")
            
            # Generate response using Gemini (run in executor to avoid blocking)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, self.model.generate_content, prompt
            )
            
            # Extract text from response
            report = response.text if hasattr(response, "text") else str(response)
            
            # Ensure report follows the required structure
            report = self._ensure_report_structure(report, sector)
            
            logger.info(f"Market report generated successfully for sector: {sector}")
            return report
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to generate report for sector {sector}: {error_type}: {error_msg}")
            logger.error(f"Full error details: {repr(e)}")
            # Return a structured error report with detailed error info
            return self._generate_error_report(sector, f"{error_type}: {error_msg}")
    
    def _build_context(self, sector: str, market_data: List[Dict[str, str]]) -> str:
        """
        Build context string from market data.
        
        Args:
            sector: Sector name
            market_data: List of market data dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = [f"# Market Data for {sector.title()} Sector in India\n"]
        
        if not market_data:
            context_parts.append("No recent market data available.")
        else:
            for i, item in enumerate(market_data, 1):
                title = item.get("title", "No title")
                snippet = item.get("snippet", "No description")
                url = item.get("url", "")
                
                context_parts.append(f"## Source {i}: {title}\n")
                context_parts.append(f"{snippet}\n")
                if url:
                    context_parts.append(f"URL: {url}\n")
                context_parts.append("\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, sector: str, context: str) -> str:
        """
        Create prompt for Gemini API.
        
        Args:
            sector: Sector name
            context: Market data context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a financial analyst specializing in the Indian market. Analyze the following market data and generate a comprehensive trade opportunities report for the {sector} sector in India.

{context}

Please generate a detailed Markdown report with the following EXACT section structure (use ## for main sections):

## Sector Overview
[Provide a brief overview of the {sector} sector in India, including key players, market size, and current state]

## Current Market Trends in India
[Analyze current trends, growth patterns, and market dynamics specific to India]

## Recent News & Signals
[Summarize and analyze the recent news and market signals from the provided data]

## Trade Opportunities
[Identify specific trade opportunities, investment prospects, and actionable insights]

## Risks & Challenges
[Outline potential risks, challenges, and factors that could impact the sector]

## Short-term Outlook
[Provide a short-term (3-6 months) outlook for the sector]

## Disclaimer
[Include a standard disclaimer about investment risks and that this is for informational purposes only]

Important:
- Focus specifically on the Indian market
- Be data-driven and objective
- Use clear, professional language
- Ensure all sections are present and well-structured
- The report should be ready to save as a .md file

Generate the report now:"""
        
        return prompt
    
    def _ensure_report_structure(self, report: str, sector: str) -> str:
        """
        Ensure the report has the required structure.
        
        Args:
            report: Generated report
            sector: Sector name
            
        Returns:
            Structured report with header
        """
        # Add main title if missing
        if not report.startswith("#"):
            report = f"# {sector.title()} Sector - Trade Opportunities Analysis\n\n{report}"
        
        # Ensure disclaimer is present
        if "## Disclaimer" not in report and "# Disclaimer" not in report:
            disclaimer = """
## Disclaimer

This analysis is for informational purposes only and does not constitute financial, investment, or trading advice. Market conditions are subject to change, and past performance does not guarantee future results. Please conduct your own research and consult with qualified financial advisors before making any investment decisions. The author and service provider are not responsible for any losses incurred based on this information.
"""
            report += disclaimer
        
        return report
    
    def _generate_error_report(self, sector: str, error_message: str) -> str:
        """
        Generate a structured error report when AI generation fails.
        
        Args:
            sector: Sector name
            error_message: Error message
            
        Returns:
            Structured error report
        """
        return f"""# {sector.title()} Sector - Trade Opportunities Analysis

## Sector Overview

Analysis temporarily unavailable.

## Current Market Trends in India

Unable to generate analysis at this time.

## Recent News & Signals

Data collection in progress.

## Trade Opportunities

Please try again later or contact support.

## Risks & Challenges

Standard market risks apply. Please exercise caution.

## Short-term Outlook

Unable to provide outlook at this time.

## Disclaimer

This analysis could not be completed due to technical issues: {error_message}

**Note**: This is an error report. Please retry your request or contact support if the issue persists.

---

Generated at: {datetime.now().isoformat()}
"""

