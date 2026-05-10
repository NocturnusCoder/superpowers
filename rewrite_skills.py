#!/usr/bin/env python3
"""
Rewrite Superpowers SKILL.md files from Claude Code tools to Agent Zero equivalents.
Preserves ALL methodology content - only changes tool references and JSON examples.
"""

import os
import re
import shutil

SOURCE_DIR = "./skills"
OUTPUT_DIR = "./skills-adapted"

SKILL_NAMES = [
    "brainstorming",
    "dispatching-parallel-agents",
    "executing-plans",
    "finishing-a-development-branch",
    "receiving-code-review",
    "requesting-code-review",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "using-git-worktrees",
    "using-superpowers",
    "verification-before-completion",
    "writing-plans",
    "writing-skills",
]

def sp_name(name):
    return f"sp-{name}"

def rewrite_skill_frontmatter(content, skill_name):
      return re.sub(
          rf'(^name:\s*){re.escape(skill_name)}(\s*$)',
          rf'\g<1>sp-{skill_name}\2',
          content,
          count=1,
          flags=re.MULTILINE,
      )

def rewrite_cross_references(content):
    """Replace superpowers:X -> sp-X and update bare skill name references."""
    for name in SKILL_NAMES:
        content = content.replace(f"superpowers:{name}", sp_name(name))
    return content


def rewrite_tool_names(content):
    """Replace Claude Code tool names with Agent Zero equivalents."""
    # Skill tool
    content = content.replace("the `Skill` tool", "the `skills_tool:load` tool")
    content = content.replace("the Skill tool", "the skills_tool:load tool")
    content = content.replace('"Invoke Skill tool"', '"Use skills_tool:load"')
    content = content.replace("Invoke Skill tool", "Use skills_tool:load")
    
    # Read tool
    content = content.replace("the Read tool", "the text_editor:read tool")
    content = content.replace("Read tool", "text_editor:read")
    
    # Edit tool
    content = content.replace("the Edit tool", "the text_editor:patch tool")
    content = content.replace("Edit tool", "text_editor:patch")
    
    # Write tool
    content = content.replace("the Write tool", "the text_editor:write tool")
    content = content.replace("Write tool", "text_editor:write")
    
    # Bash tool
    content = content.replace("the Bash tool", "the code_execution_tool")
    content = content.replace("Bash tool", "code_execution_tool")
    
    # Task tool
    content = content.replace("the Task tool", "the call_subordinate tool")
    content = content.replace("Task tool (general-purpose)", "call_subordinate tool")
    content = content.replace("Task tool (superpowers:code-reviewer)", "call_subordinate tool (with code reviewer context)")
    content = content.replace("Task tool", "call_subordinate tool")
    content = content.replace("Use Task tool", "Use call_subordinate")
    content = content.replace("Use the Task tool", "Use call_subordinate")
    
    # find-skills
    content = content.replace("find-skills", "skills_tool:list")
    
    # TodoWrite -> thoughts array
    content = content.replace("Create TodoWrite with all tasks", "Track all tasks in thoughts array")
    content = content.replace("Create TodoWrite and proceed", "Track tasks in thoughts array and proceed")
    content = content.replace("Create TodoWrite", "Track progress in thoughts array")
    content = content.replace("Create a TodoWrite", "Track progress in thoughts array")
    content = content.replace("Mark task complete in TodoWrite", "Mark task complete in thoughts")
    content = content.replace("Mark task complete in thoughts array", "Mark task complete in thoughts")
    content = content.replace("todo per item", "item in thoughts")
    content = content.replace("TodoWrite", "thoughts array")
    
    return content


def rewrite_using_superpowers(content):
    """Special rewrite for the meta-skill."""
    
    # Replace "How to Access Skills" section
    old_section = """## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you\u2014follow it directly. Never use the Read tool on skill files.

**In Gemini CLI:** Skills activate via the `activate_skill` tool. Gemini loads skill metadata at session start and activates the full content on demand.

**In other environments:** Check your platform's documentation for how skills are loaded.

## Platform Adaptation

Skills use Claude Code tool names. Non-CC platforms: see `references/codex-tools.md` (Codex) for tool equivalents. Gemini CLI users get the tool mapping loaded automatically via GEMINI.md."""
    
    new_section = """## How to Access Skills

**In Agent Zero:** Use `skills_tool:load` to load a skill by name. When you invoke a skill, its content is loaded and presented to you\u2014follow it directly.

Example:
```json
{
    "thoughts": ["Need to check if a skill applies..."],
    "headline": "Loading relevant skill",
    "tool_name": "skills_tool:load",
    "tool_args": {"skill_name": "sp-brainstorming"}
}
```

To list all available skills:
```json
{
    "thoughts": ["Listing available skills..."],
    "headline": "Listing skills",
    "tool_name": "skills_tool:list",
    "tool_args": {}
}
```

## Platform Adaptation

These skills are adapted for Agent Zero. Tool references use Agent Zero JSON format natively. All skill names use the `sp-` prefix (e.g., `sp-brainstorming`, `sp-test-driven-development`)."""
    
    content = content.replace(old_section, new_section)
    
    # Replace instruction priority line
    content = content.replace(
        "1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) \u2014 highest priority",
        "1. **User's explicit instructions** (direct requests, project instructions) \u2014 highest priority"
    )
    
    # Replace TodoWrite in flowchart labels
    content = content.replace('"Create TodoWrite todo per item"', '"Track checklist items in thoughts array"')
    content = content.replace("Create TodoWrite todo per item", "Track checklist items in thoughts array")
    
    # Replace Skill tool invocation in flowchart
    content = content.replace('"Invoke Skill tool"', '"Use skills_tool:load"')
    content = content.replace("Invoke Skill tool", "Use skills_tool:load")
    
    return content


def rewrite_dispatching_parallel(content):
    """Replace the TypeScript Task() dispatch example with Agent Zero JSON."""
    old_example = """```typescript
// In Claude Code / AI environment
Task(\"Fix agent-tool-abort.test.ts failures\")
Task(\"Fix batch-completion-behavior.test.ts failures\")
Task(\"Fix tool-approval-race-conditions.test.ts failures\")
// All three run concurrently
```"""
    
    new_example = """```json
// In Agent Zero - dispatch parallel subordinates (use different session numbers)
{"thoughts": ["Dispatching parallel agent for abort tests"], "headline": "Fix abort tests", "tool_name": "call_subordinate", "tool_args": {"message": "Fix agent-tool-abort.test.ts failures", "reset": "true", "profile": "developer"}}
{"thoughts": ["Dispatching parallel agent for batch tests"], "headline": "Fix batch tests", "tool_name": "call_subordinate", "tool_args": {"message": "Fix batch-completion-behavior.test.ts failures", "reset": "true", "profile": "developer"}}
{"thoughts": ["Dispatching parallel agent for race condition tests"], "headline": "Fix race condition tests", "tool_name": "call_subordinate", "tool_args": {"message": "Fix tool-approval-race-conditions.test.ts failures", "reset": "true", "profile": "developer"}}
// Each subordinate runs independently with isolated context
```"""
    
    content = content.replace(old_example, new_example)
    return content


def rewrite_executing_plans(content):
    """Special rewrites for executing-plans."""
    content = content.replace(
        "Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers:subagent-driven-development instead of this skill.",
        "Note: Superpowers works best with subagent support. If subagents are available, use sp-subagent-driven-development instead of this skill."
    )
    return content


def rewrite_writing_skills(content):
    """Special rewrites for writing-skills."""
    content = content.replace(
        "**Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code, `~/.agents/skills/` for Codex)**",
        "**Skills live in `/a0/usr/skills/` with `sp-` prefix for Agent Zero compatibility**"
    )
    content = content.replace(
        "**IMPORTANT: Use TodoWrite to create todos for EACH checklist item below.**",
        "**IMPORTANT: Track each checklist item in your thoughts array as you work through them.**"
    )
    return content


def rewrite_brainstorming(content):
    """Special rewrites for brainstorming."""
    content = content.replace(
        "`skills/brainstorming/visual-companion.md`",
        "`sp-brainstorming/visual-companion.md`"
    )
    return content


def rewrite_subagent_prompts(content):
    """Rewrite subagent prompt template files."""
    # These files have patterns like:
    # Task tool (general-purpose):
    #   description: "..."
    #   prompt: |
    # which become:
    # call_subordinate tool:
    #   message: |
    
    # Fix description+prompt patterns
    content = re.sub(
        r'call_subordinate tool:\s*\n\s*description:\s*"[^"]*"\s*\n\s*prompt:\s*\|',
        'call_subordinate tool:\n  message: |',
        content
    )
    return content


def rewrite_code_reviewer(content):
    """Rewrite the code-reviewer.md template."""
    # The template is mostly fine - it uses bash commands and git diffs
    # which work as-is in code_execution_tool
    # Just update cross-references
    return content


def process_skill(skill_name):
    """Process a single skill directory."""
    src_dir = os.path.join(SOURCE_DIR, skill_name)
    dst_dir = os.path.join(OUTPUT_DIR, sp_name(skill_name))
    
    if not os.path.exists(src_dir):
        print(f"  WARNING: {src_dir} does not exist, skipping")
        return
    
    # Clean and create output dir
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        dst_root = os.path.join(dst_dir, rel_path) if rel_path != "." else dst_dir
        if rel_path != ".":
            os.makedirs(dst_root, exist_ok=True)
        
        for filename in files:
            src_file = os.path.join(root, filename)
            dst_file = os.path.join(dst_root, filename)
            
            is_skill_md = filename == "SKILL.md"
            is_prompt = filename.endswith(("-prompt.md", "reviewer.md"))
            
            if is_skill_md or is_prompt:
                with open(src_file, "r") as f:
                    content = f.read()
                
                # Apply all transformations
                content = rewrite_cross_references(content)
                content = rewrite_tool_names(content)
                
                # Skill-specific rewrites
                if is_skill_md:
                    content = rewrite_skill_frontmatter(content, skill_name)
                    if skill_name == "using-superpowers":
                        content = rewrite_using_superpowers(content)
                    elif skill_name == "dispatching-parallel-agents":
                        content = rewrite_dispatching_parallel(content)
                    elif skill_name == "executing-plans":
                        content = rewrite_executing_plans(content)
                    elif skill_name == "writing-skills":
                        content = rewrite_writing_skills(content)
                    elif skill_name == "brainstorming":
                        content = rewrite_brainstorming(content)
                
                if is_prompt:
                    content = rewrite_subagent_prompts(content)
                    if "code-reviewer" in filename:
                        content = rewrite_code_reviewer(content)
                
                # Fix any double sp- prefixes
                content = content.replace("sp-sp-", "sp-")
                
                with open(dst_file, "w") as f:
                    f.write(content)
                
                print(f"  REWRITTEN: {sp_name(skill_name)}/{filename}")
            else:
                # Copy supporting files as-is
                shutil.copy2(src_file, dst_file)
                print(f"  COPIED: {sp_name(skill_name)}/{filename}")


def main():
    print("=== Superpowers SKILL.md Rewriter for Agent Zero ===")
    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for skill_name in SKILL_NAMES:
        print(f"\nProcessing: {skill_name}")
        process_skill(skill_name)
    
    # Summary
    print("\n=== Rewrite Complete ===")
    total_files = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        total_files += len(files)
    print(f"Total files in output: {total_files}")
    
    # List structure
    print("\n=== Output Structure ===")
    for skill_name in SKILL_NAMES:
        dst_dir = os.path.join(OUTPUT_DIR, sp_name(skill_name))
        if os.path.exists(dst_dir):
            files = []
            for r, d, fs in os.walk(dst_dir):
                for f in fs:
                    rel = os.path.relpath(os.path.join(r, f), dst_dir)
                    files.append(rel)
            print(f"  {sp_name(skill_name)}/ ({len(files)} files): {', '.join(files)}")


if __name__ == "__main__":
    main()
