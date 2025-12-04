# Contributing to PartitionFinder Python 3

Thank you for your interest in contributing! 🎉

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Fix issues
- ✨ Add new features
- 🧪 Add tests

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/yourusername/partitionfinder-python3.git
cd partitionfinder-python3
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Test the GUI
python gui_app.py

# Test command line
python PartitionFinder.py examples/nucleotide
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

## Development Guidelines

### Code Style

- Follow **PEP 8** style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Python Compatibility

- Ensure code works on **Python 3.8 - 3.12+**
- Avoid Python 2 specific syntax
- Test on Windows, macOS, and Linux if possible

### Testing

Before submitting:

```bash
# Test with examples
python PartitionFinder.py examples/nucleotide
python PartitionFinderProtein.py examples/aminoacid
python PartitionFinderMorphology.py examples/morphology

# Test GUI
python gui_app.py
```

### Commit Messages

Use clear, descriptive commit messages:

```
✅ Good:
- "Fix NEXUS parser for interleaved format"
- "Add progress bar to GUI analysis"
- "Update numpy dependency to 1.21.0"

❌ Avoid:
- "Fixed stuff"
- "Update"
- "Changes"
```

## Pull Request Process

### 1. Before Submitting

- [ ] Code follows PEP 8 style
- [ ] All tests pass
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear
- [ ] No unnecessary files included

### 2. Submit Pull Request

1. Push your branch to GitHub
2. Go to the repository and click "New Pull Request"
3. Fill out the PR template:
   - **Title**: Clear description of changes
   - **Description**: What and why
   - **Testing**: How you tested
   - **Issues**: Link related issues (#123)

### 3. Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, it will be merged

## Areas Needing Help

### High Priority

- 🐛 **Bug Fixes**: Any reported issues
- 📝 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Add unit tests
- 🌐 **macOS/Linux**: Test and fix platform-specific issues

### Feature Ideas

- 🎨 **GUI Improvements**: More features, better UX
- 📊 **Visualization**: Plot results in GUI
- ⚡ **Performance**: Optimize slow operations
- 🔧 **Configuration**: More analysis options
- 🌍 **Internationalization**: Multi-language support

## Bug Reports

When reporting bugs, include:

1. **Python version**: `python --version`
2. **Operating System**: Windows 10/11, macOS, Linux
3. **PartitionFinder version**: From `VERSION.txt`
4. **Steps to reproduce**: Detailed instructions
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full traceback if applicable
8. **Input files**: Sample data if relevant (or sanitized version)

### Bug Report Template

```markdown
**Python Version**: 3.10.0
**OS**: Windows 11
**PartitionFinder Version**: 2.1.1 Python 3

**Description**:
[Clear description of the bug]

**Steps to Reproduce**:
1. Open GUI
2. Load file X
3. Click analyze
4. Error appears

**Expected**: Analysis completes successfully
**Actual**: Error message "..."

**Error Log**:
```
[Paste error here]
```

**Files Used**: [Attach or describe]
```

## Feature Requests

When suggesting features:

1. **Use case**: Why is this needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered?
4. **Priority**: Nice-to-have or critical?

## Documentation Contributions

Help improve documentation:

- Fix typos and grammar
- Add examples
- Clarify confusing sections
- Add screenshots
- Translate to other languages

## Code of Conduct

### Be Respectful

- Be kind and courteous
- Respect different viewpoints
- Accept constructive criticism
- Focus on what's best for the community

### Be Collaborative

- Help others when you can
- Share knowledge and resources
- Give credit where due
- Welcome newcomers

### Be Professional

- Use welcoming and inclusive language
- Stay on topic
- No harassment or trolling
- Follow GitHub's Community Guidelines

## Questions?

- **General Questions**: Open a [Discussion](../../discussions)
- **Bug Reports**: Open an [Issue](../../issues)
- **Security Issues**: Email directly (don't open public issue)

## Thank You! 🙏

Every contribution helps make PartitionFinder better for the phylogenetics community!

---

**Happy Contributing!** 🎉
