class CLIInterface:
    def prompt(self, message):
        return input(f"{message}: ").strip()

    def display(self, message):
        print(message)

    def display_dns_instructions(self, tokens):
        self.display("--- DNS Validation Required ---")
        self.display(f"DIAGNOSTIC: tokens={tokens}")
        self.display("Please add the following TXT records to your DNS provider:")
        for token_info in tokens:
            self.display(f"DIAGNOSTIC: token_info={token_info}")
            # Assuming for now it might be more than 2, need to see the structure
        self.display("-------------------------------")
        input("Press Enter after you have updated the DNS records and they have propagated...")
