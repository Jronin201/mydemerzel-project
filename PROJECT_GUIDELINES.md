# 🎯 Demerzel Project Guidelines

**Comprehensive development and design guidelines for the TTRPG Chatbot project**

## 🎮 Project Overview

This is a Flask-based AI-assisted TTRPG chatbot system **optimized specifically for Windows 11 PCs**. All development decisions should prioritize desktop PC environments over mobile compatibility.

## 🖥️ Core Platform Requirements

### **Primary Target Platform**

- **OS**: Windows 11 (Optimized)
- **Browsers**: Edge (recommended), Chrome 90+, Firefox 85+, Opera 75+
- **Input**: Keyboard and mouse (not touch)
- **Display**: Desktop monitors (1920x1080+, wide-screen support)

### **Design Philosophy**

- **PC-First**: All UI/UX decisions prioritize desktop experience
- **No Mobile**: Mobile compatibility is explicitly removed
- **Clean Code**: Regular cleanup of redundant and orphaned code
- **Accessibility**: WCAG 2.1 AA compliance with screen reader support

## 🏗️ Architecture Standards

### **File Organization**

```
/static/ttrpg-chatbot/           # Main interface
/static/<ttrpg-name>/            # Individual TTRPG modules
/docs/                           # Documentation
/scripts/                        # Management utilities
```

### **Code Quality Standards**

- **No Duplicate Code**: Remove redundant functions and CSS
- **No Orphaned Code**: Delete unused functions, variables, and styles
- **Consistent Comments**: Update comments to match actual implementation
- **PC-Optimized Values**: Font sizes 1.0em+, wider padding, larger click targets

## 🎨 UI/UX Design Guidelines

### **Layout Structure**

- **3-Column Grid**: `250px 1fr 40%` (buttons | character info | chat)
- **Button Column**: 20 quick-action buttons, full width, 1.0em font
- **Chat Area**: 40% of monitor width for PC optimization
- **Character Info**: Flexible middle column with auto-resize textareas

### **Visual Design Standards**

- **Color Scheme**: Dark theme (#121212 background, #e0e0e0 text)
- **Typography**: Segoe UI font family, 1.15em base font size
- **Spacing**: Generous padding/margins for desktop use
- **Interactive Elements**: Clear hover states, 8px border radius

### **Enhanced Formatting**

- **Markdown Support**: Full markdown parsing with custom CSS
- **Emoji Integration**: Contextual emojis for game terms
- **Dice Rolls**: `1d20+3` → 🎲 **1d20+3**
- **Status Effects**: Purple gradient highlighting
- **Character Stats**: Blue gradient highlighting

## 🚀 Development Workflow

### **Essential Commands**

```bash
./start.sh                       # Development server (hot reload, debug mode)
./deploy.sh                      # Production deployment (Gunicorn)
./deploy.sh --dev                # Production deps + dev server
./backup.sh                      # Backup character data
python scripts/show_commands.py  # List all commands
./shortcuts.sh status            # Project overview
```

### **Environment Setup**

```bash
cp .env.example .env             # Copy environment template
nano .env                        # Edit with your settings
# Required: FLASK_SECRET_KEY, OPENAI_API_KEY
```

### **TTRPG Management**

```bash
# Register new TTRPG
python scripts/register_ttrpg.py register \
  --name "system-name" \
  --display-name "Display Name" \
  --description "Brief description"

# Test all systems
python scripts/test_ttrpg_integration.py
```

### **Code Standards**

- **Clean Commits**: Descriptive commit messages
- **Regular Cleanup**: Remove mobile code remnants
- **Function Separation**: No duplicate functionality
- **Comment Accuracy**: Comments must match implementation

## 🔧 Technical Specifications

### **Frontend Stack**

- **HTML5**: Semantic markup with ARIA labels
- **CSS3**: Grid layout, modern features (no prefixes needed)
- **JavaScript**: ES6+, IIFE patterns, no mobile event handlers
- **Dependencies**: Marked.js for markdown, no mobile libraries

### **Backend Stack**

- **Python 3.8+**: Flask application with OpenAI integration
- **Requirements**: Use `requirements-prod.txt` for deployment
- **Environment**: `DEPLOYMENT_ENV=render` for production

### **Deployment Standards**

- **Gunicorn**: Production WSGI server with PC-optimized config
- **Memory Optimization**: Single worker for embeddings efficiency
- **Environment Variables**: All secrets in environment, not code
- **Git Configuration**: Automated for deployment environments

## 🧹 Code Cleanup Guidelines

### **What to Remove**

- ✅ Mobile-specific CSS (viewport meta, responsive breakpoints)
- ✅ Touch event handlers (touchstart, touchend, etc.)
- ✅ Webkit prefixes and mobile browser compatibility
- ✅ Duplicate functions with identical logic
- ✅ Orphaned CSS selectors with no corresponding HTML
- ✅ Unused variables and commented-out code

### **What to Optimize**

- ✅ Font sizes for desktop viewing (1.0em minimum)
- ✅ Button padding for mouse interaction (0.8em+ padding)
- ✅ Grid layouts for wide screens
- ✅ Hover states for desktop interaction
- ✅ Comments to match actual implementation

## 🎲 TTRPG Integration Standards

### **System Module Structure**

```
/static/<ttrpg-name>/
├── system_prompt.txt           # Required: AI behavior definition
├── index.html                  # Optional: Custom interface
├── css/style.css              # Optional: TTRPG-specific styling
├── images/                     # Optional: TTRPG-specific images
└── js/custom.js               # Optional: Custom JavaScript
```

### **Adding New TTRPG Systems**

```bash
# Step 1: Register new TTRPG
python scripts/register_ttrpg.py register \
  --name "system-name" \
  --display-name "Display Name" \
  --description "Brief description"

# Step 2: Create system prompt
nano static/system-name/system_prompt.txt

# Step 3: Test integration
python scripts/test_ttrpg_integration.py --ttrpg system-name

# Step 4: Restart server
./deploy.sh  # or ./start.sh for development
```

### **System Prompt Template**

```
You are the [GM Title] for [TTRPG Name], [description].

Tone: [Atmospheric description]
Goals: [Primary objectives]
Mechanics: [Game system specifics]
Setting Guidelines: [Setting-specific instructions]
Character Creation: [How to guide character creation]
Restrictions: [What to avoid]

Never break character. This is the world of [TTRPG Name].
Respond only in-character unless asked for out-of-character help.
```

### **Directory Naming Standards**

- Use lowercase with hyphens: `call-of-cthulhu`, `vampire-the-masquerade`
- No spaces or special characters
- Keep names concise but descriptive

### **Button Text Standards**

- 20 action buttons in `/static/ttrpg-chatbot/button-texts/`
- Short, action-oriented phrases
- TTRPG-appropriate language
- Files named `button1.txt` through `button20.txt`

## 📊 Quality Assurance

### **Before Every Commit**

1. **Remove redundant code**: Check for duplicates
2. **Update comments**: Ensure accuracy
3. **Test PC interface**: Verify desktop experience
4. **Validate accessibility**: Screen reader compatibility
5. **Check deployment**: Ensure production readiness

### **Testing Checklist**

- ✅ All 20 buttons visible and functional
- ✅ 3-column layout working on desktop
- ✅ No mobile CSS or JavaScript
- ✅ Proper font sizes for PC viewing
- ✅ Hover states working correctly
- ✅ No duplicate functions or styles

## 🛡️ Security & Performance

### **Security Requirements**

- Environment variables for all secrets
- Input validation on all user data
- CSP headers for XSS protection
- No hardcoded API keys or passwords

### **Performance Standards**

- Single worker for memory efficiency
- Embedding caching for faster responses
- Optimized CSS delivery
- Minimal JavaScript footprint

---

**Key Principle**: Every decision should optimize for Windows 11 PC users with desktop monitors, keyboard/mouse input, and modern desktop browsers. Mobile compatibility is explicitly not supported.
