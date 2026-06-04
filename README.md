# NVAC (Non-Visual ACME Client)

NVAC is a user-friendly, accessible, text-based utility for generating SSL/TLS certificates via the ACME protocol and Let's Encrypt. 

Designed for accessibility, NVAC provides a streamlined, non-visual interface (TUI/GUI using wxPython) to manage certificate issuance using DNS validation.

## Features
- **Accessible Interface:** Built with wxPython for native screen-reader compatibility and keyboard navigation.
- **DNS-01 Validation:** Dedicated challenge management with propagation checking.
- **Full Control:** Generate, verify, copy, and save your certificates and private keys.
- **Accessibility Focus:** Clear UI labels, tab-navigable fields, and screen-reader friendly dialogs.

## Installation

### Prerequisites
- Python 3.x
- `pip`

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/averlice/nvac.git
   cd nvac
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage
NVAC guides you through the process of requesting a certificate.
1. Enter your domains (comma-separated).
2. Enter your email address.
3. Handle the DNS-01 challenge by adding the provided TXT records to your DNS provider.
4. Verify propagation and finish to save your certificate and private key.

## License
NVAC is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for more details.
