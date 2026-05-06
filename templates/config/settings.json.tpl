{
  "permissions": {
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(git push --force origin main)",
      "Bash(git push --force origin master)",
      "Bash(git reset --hard HEAD~*)",
      "Bash(chmod -R 777 *)",
      "Bash(sudo rm *)",
      "Bash(del /f /s /q C:\\*)",
      "Bash(rd /s /q C:\\*)"
    ]
  },
  "model": "opusplan",
  "env": {
    "ECC_MCP_HEALTH_FAIL_OPEN": "true"
  },
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python {{HOME}}/.claude/scripts/model_router.py",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"{{HOME}}/.pixel-agents/hooks/claude-hook.js\"",
            "timeout": 5
          }
        ]
      }
    ]
  },
  "enabledPlugins": {
    "telegram@claude-plugins-official": true,
    "discord@claude-plugins-official": true,
    "claude-mem@thedotmack": true,
    "superpowers@claude-plugins-official": true,
    "everything-claude-code@everything-claude-code": true,
    "marketing-skills@marketingskills": true,
    "warp@claude-code-warp": true
  },
  "extraKnownMarketplaces": {
    "thedotmack": {
      "source": {
        "source": "github",
        "repo": "thedotmack/claude-mem"
      }
    },
    "everything-claude-code": {
      "source": {
        "source": "git",
        "url": "https://github.com/affaan-m/everything-claude-code.git"
      }
    },
    "marketingskills": {
      "source": {
        "source": "github",
        "repo": "coreyhaines31/marketingskills"
      }
    },
    "claude-code-warp": {
      "source": {
        "source": "github",
        "repo": "warpdotdev/claude-code-warp"
      }
    }
  },
  "voice": {
    "enabled": true,
    "mode": "hold"
  },
  "theme": "dark-ansi",
  "voiceEnabled": true,
  "effortLevel": "low"
}
