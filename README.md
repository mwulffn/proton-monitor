# Proton Mintor

This repository provides a simple Python script (`main.py`) that uses the unofficial [`protonmail`](https://pypi.org/project/protonmail/) library to log in to ProtonMail, read messages from the inbox, and apply custom filters (e.g., trashing certain emails, moving them to specific labels). The script makes it easy to automatically organize your ProtonMail inbox.

## Features

- **Session Persistence**: The script saves your session data to a `.proton-session` file so you don't have to log in every time.
- **Automatic Filtering**: Various filters (found in `filters.py`) can detect and handle:
  - Review solicitations
  - Shipping updates
  - Social media notifications (with special handling for LinkedIn)
  - Takeaway/food order emails
- **Labeling & Moving**: The script can automatically apply or remove labels, trash emails, and move them to different folders.

## Setup and Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Sync Dependencies**  
   Instead of installing Python packages manually, use `uv sync` to set up the environment. This command (provided by your `uv` tool) will read the project requirements and prepare everything needed:
   ```bash
   uv sync
   ```

3. *(Optional)* **Set Up Environment Variables**  
   You can supply your ProtonMail username and password as real environment variables (e.g., in your shell) or in a `.env` file. For example, create a `.env` file in the project’s root directory with:
   ```env
   PROTON_USERNAME=your-username
   PROTON_PASSWORD=your-password
   ```
   > **Note**: Make sure you **never** commit `.env` files or any sensitive credentials to version control.  
   If you do not configure these environment variables, you will be prompted to enter your credentials when the script runs.

## How to Run

1. **Restore or Create a Session**  
   - The script checks for a saved session in `.proton-session`.  
   - If no session is found, it will use your environment variables (if set) or prompt you for credentials interactively.  
   - It will then save the session for future runs.

2. **Run Using `uv`**  
   Use the `uv` tool to run the script:
   ```bash
   uv main.py
   ```
   Follow any on-screen prompts for credentials if needed.

3. **Observe the Logs**  
   - The script uses Python’s built-in logging (`logging.basicConfig(level=logging.INFO)`), so you’ll see informational messages about the script’s progress (e.g., loading labels, moving messages, etc.).

## Customizing the Filters

You can customize or add new filters to suit your needs. In `filters.py` (not shown here, but referenced in the code):

1. Create a new function, e.g., `is_custom_condition(message)` that returns `True` or `False` based on your criteria.
2. In `apply_filters(message)`, add a conditional block:
   ```python
   if is_custom_condition(message):
       # Take any action here, e.g. move_message, trash_message, apply_label, etc.
       return
   ```

## Contributing

Contributions are welcome! Feel free to open issues or pull requests if you find bugs or want to add features.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/new-filter`
3. Commit your changes: `git commit -m 'Add new custom filter'`
4. Push to the branch: `git push origin feature/new-filter`
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer**: This script relies on an unofficial ProtonMail library, which may break if ProtonMail changes its internal APIs. Use at your own risk. Always be cautious when handling credentials and sensitive data.