import simple_acme_dns

class ACMEClient:
    def __init__(self, domains, email, directory="https://acme-staging-v02.api.letsencrypt.org/directory"):
        self.domains = domains
        self.email = email
        self.directory = directory
        self.client = None

    def initialize(self):
        self.client = simple_acme_dns.ACMEClient(
            domains=self.domains,
            email=self.email,
            directory=self.directory,
            new_account=True,
            generate_csr=True
        )

    def get_tokens(self):
        if not self.client:
            raise Exception("Client not initialized")
        return self.client.request_verification_tokens()

    def request_certificate(self):
        if not self.client:
            raise Exception("Client not initialized")
        return self.client.request_certificate()

    @property
    def private_key(self):
        if not self.client:
            raise Exception("Client not initialized")
        return self.client.private_key
