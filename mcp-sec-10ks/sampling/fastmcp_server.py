#!/usr/bin/env python3
"""
Simple FastMCP Server with Sampling Support
"""
from fastmcp import FastMCP, Context

# Create the MCP server
mcp = FastMCP("simple-sampling-server")

@mcp.tool()
async def ask_question(question: str, ctx: Context) -> str:
    """
    A simple tool that uses sampling to answer questions via LLM
    """
    # Log the start of processing
    await ctx.info(f"🔄 Processing question: '{question}'")
    
    # Validate the question
    if not question or len(question.strip()) < 3:
        await ctx.error("❌ Question is too short or empty")
        return "Error: Please provide a valid question with at least 3 characters."
    
    # Log question analysis
    question_length = len(question)
    await ctx.info(f"📏 Question length: {question_length} characters")
    
    if question_length > 200:
        await ctx.info("⚠️ Long question detected - this may take more time to process")
    
    # Create a simple prompt
    prompt = f"""Please answer the following question in a helpful and concise way:

Question: {question}

Please provide a clear and informative answer."""
    
    # Log before sampling
    await ctx.info("🤖 Sending request to LLM for processing...")
    
    try:
        # Use sampling to get LLM response via the Context
        result = await ctx.sample(prompt, max_tokens=500, temperature=0.7)
        
        # Log successful completion
        response_length = len(result.text) if result.text else 0
        await ctx.info(f"✅ LLM response received - {response_length} characters")
        
        if response_length == 0:
            await ctx.error("❌ Empty response received from LLM")
            return "Error: Received empty response from LLM. Please try again."
        
        # Log completion
        await ctx.info("🎯 Question processing completed successfully")
        
        return f"Answer: {result.text}"
        
    except Exception as e:
        await ctx.error(f"❌ Error during LLM sampling: {str(e)}")
        return f"Error: Failed to process question - {str(e)}"

@mcp.tool()
def greet(name: str) -> str:
    """Simple greeting tool (no sampling)"""
    return f"Hello, {name}! This is FastMCP server."

@mcp.tool()
async def test_logging(message: str, ctx: Context) -> str:
    """
    Test all logging levels available in FastMCP Context
    """
    await ctx.info(f"ℹ️ INFO: Testing logging with message: '{message}'")
    await ctx.error(f"❌ ERROR: This is a test error (not a real error)")
    
    # Test different scenarios
    if "debug" in message.lower():
        await ctx.info("🐛 DEBUG-style info: Debug mode detected in message")
    
    if "warning" in message.lower():
        await ctx.info("⚠️ WARNING-style info: Warning detected in message")
        
    if "success" in message.lower():
        await ctx.info("✅ SUCCESS: Success keyword detected")
    
    # Log some processing steps
    await ctx.info("📊 Processing step 1: Message analysis complete")
    await ctx.info("📊 Processing step 2: Keyword detection complete")
    await ctx.info("📊 Processing step 3: Response preparation complete")
    
    return f"Logging test completed for message: '{message}'. Check the logs above!"

if __name__ == "__main__":
    mcp.run()
