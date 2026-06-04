import wx
import wx.adv
import dns.resolver
from acme_client import ACMEClient

class DNSChallengeDialog(wx.Dialog):
    def __init__(self, parent, tokens):
        super().__init__(parent, title="DNS Validation", size=(600, 450))
        self.tokens = tokens
        self.validated_domains = set()
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.info_label = wx.StaticText(panel, label="Select a domain to view records:")
        sizer.Add(self.info_label, 0, wx.ALL, 5)

        self.list_ctrl = wx.ListBox(panel, size=(-1, 120))
        for domain, token in self.tokens:
            self.list_ctrl.Append(domain)
        self.list_ctrl.Bind(wx.EVT_LISTBOX, self.on_select)
        sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Record Name Section
        sizer.Add(wx.StaticText(panel, label="Record Name:"), 0, wx.ALL, 5)
        self.name_input = wx.TextCtrl(panel, style=wx.TE_READONLY)
        sizer.Add(self.name_input, 0, wx.ALL | wx.EXPAND, 5)
        
        self.copy_name_btn = wx.Button(panel, label="Copy Record Name")
        self.copy_name_btn.Bind(wx.EVT_BUTTON, lambda evt: self.copy_to_clipboard(self.name_input.GetValue(), "Record Name"))
        sizer.Add(self.copy_name_btn, 0, wx.ALL, 5)

        # Record Value Section
        sizer.Add(wx.StaticText(panel, label="TXT Value:"), 0, wx.ALL, 5)
        self.value_input = wx.TextCtrl(panel, style=wx.TE_READONLY)
        sizer.Add(self.value_input, 0, wx.ALL | wx.EXPAND, 5)

        self.copy_value_btn = wx.Button(panel, label="Copy TXT Value")
        self.copy_value_btn.Bind(wx.EVT_BUTTON, self.on_copy_value)
        sizer.Add(self.copy_value_btn, 0, wx.ALL, 5)

        # Actions
        self.check_btn = wx.Button(panel, label="Check Propagation")
        self.check_btn.Bind(wx.EVT_BUTTON, self.on_check)
        sizer.Add(self.check_btn, 0, wx.ALL, 10)

        self.finish_btn = wx.Button(panel, label="Finish")
        self.finish_btn.Bind(wx.EVT_BUTTON, self.on_finish)
        self.finish_btn.Disable()
        sizer.Add(self.finish_btn, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

    def on_copy_value(self, event):
        self.copy_to_clipboard(self.value_input.GetValue(), "TXT Value")

    def on_select(self, event):
        index = self.list_ctrl.GetSelection()
        domain, token_list = self.tokens[index]
        
        # Ensure we convert the list to a string
        token_str = token_list[0] if isinstance(token_list, (list, tuple)) else str(token_list)
        
        self.name_input.SetValue(domain)
        self.value_input.SetValue(token_str)

    def copy_to_clipboard(self, text, label):
        if text:
            clipboard = wx.Clipboard.Get()
            if clipboard.Open():
                data = wx.TextDataObject(text)
                clipboard.SetData(data)
                clipboard.Flush()
                clipboard.Close()
                wx.MessageBox(f"Copied {label} to clipboard!", "Success")
            else:
                wx.MessageBox("Could not open clipboard.", "Error")

    def on_check(self, event):
        domain = self.name_input.GetValue()
        expected_value = self.value_input.GetValue()
        
        if not domain or not expected_value:
            wx.MessageBox("Please select a domain to check.", "Info")
            return
            
        try:
            # Query Google's public DNS for the TXT record
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8']
            answers = resolver.resolve(domain, 'TXT')
            
            # Check if any record matches
            found = False
            for rdata in answers:
                for txt_string in rdata.strings:
                    # Some versions return bytes, some strings. Decode if bytes.
                    val = txt_string.decode('utf-8') if isinstance(txt_string, bytes) else txt_string
                    if val == expected_value:
                        found = True
                        break
            
            if found:
                wx.MessageBox("DNS Propagation Passed! The record is visible.", "Success")
                self.validated_domains.add(domain)
                # Check if all domains are validated
                if len(self.validated_domains) == len(self.tokens):
                    self.finish_btn.Enable()
            else:
                wx.MessageBox("DNS Propagation Failed. The record value does not match.", "Error")
                
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            wx.MessageBox("DNS Propagation Failed. The record was not found.", "Error")
        except Exception as e:
            wx.MessageBox(f"Error checking DNS: {e}", "Error")
        
    def on_finish(self, event):
        self.EndModal(wx.ID_OK)

class IssuanceResultDialog(wx.Dialog):
    def __init__(self, parent, cert, key):
        super().__init__(parent, title="Certificate Generated", size=(600, 500))
        self.cert = cert.decode('utf-8') if isinstance(cert, bytes) else cert
        self.key = key.decode('utf-8') if isinstance(key, bytes) else key
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Certificate Section
        sizer.Add(wx.StaticText(panel, label="Certificate:"), 0, wx.ALL, 5)
        self.cert_input = wx.TextCtrl(panel, value=self.cert, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        sizer.Add(self.cert_input, 0, wx.ALL | wx.EXPAND, 5)
        
        copy_cert_btn = wx.Button(panel, label="Copy Certificate")
        copy_cert_btn.Bind(wx.EVT_BUTTON, lambda evt: self.copy_to_clipboard(self.cert_input.GetValue(), "Certificate"))
        sizer.Add(copy_cert_btn, 0, wx.ALL, 5)

        # Private Key Section
        sizer.Add(wx.StaticText(panel, label="Private Key:"), 0, wx.ALL, 5)
        self.key_input = wx.TextCtrl(panel, value=self.key, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        sizer.Add(self.key_input, 0, wx.ALL | wx.EXPAND, 5)

        copy_key_btn = wx.Button(panel, label="Copy Private Key")
        copy_key_btn.Bind(wx.EVT_BUTTON, lambda evt: self.copy_to_clipboard(self.key_input.GetValue(), "Private Key"))
        sizer.Add(copy_key_btn, 0, wx.ALL, 5)

        save_btn = wx.Button(panel, label="Save All to Files")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        sizer.Add(save_btn, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

    def copy_to_clipboard(self, text, label):
        clipboard = wx.Clipboard.Get()
        if clipboard.Open():
            data = wx.TextDataObject(text)
            clipboard.SetData(data)
            clipboard.Flush()
            clipboard.Close()
            wx.MessageBox(f"Copied {label} to clipboard!", "Success")

    def on_save(self, event):
        with wx.DirDialog(self, "Select Directory to Save Files", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                path = dirDialog.GetPath()
                with open(f"{path}/certificate.pem", "w") as f:
                    f.write(self.cert)
                with open(f"{path}/private_key.pem", "w") as f:
                    f.write(self.key)
                wx.MessageBox(f"Files saved to {path}", "Success")

class NVACFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='NVAC - Accessible ACME Client', size=(400, 350))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.domain_label = wx.StaticText(panel, label="Domains (comma-separated):")
        self.domain_input = wx.TextCtrl(panel)
        sizer.Add(self.domain_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.domain_input, 0, wx.ALL | wx.EXPAND, 5)

        self.email_label = wx.StaticText(panel, label="Email address:")
        self.email_input = wx.TextCtrl(panel)
        sizer.Add(self.email_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.email_input, 0, wx.ALL | wx.EXPAND, 5)

        self.generate_btn = wx.Button(panel, label="Generate Certificate")
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        sizer.Add(self.generate_btn, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(sizer)
        self.Show()

    def on_generate(self, event):
        domains = [d.strip() for d in self.domain_input.GetValue().split(',')]
        raw_email = self.email_input.GetValue().strip()
        
        try:
            wx.BeginBusyCursor()
            self.client = ACMEClient(domains, raw_email)
            self.client.initialize()
            tokens = self.client.get_tokens()
            # Successfully got tokens, now safely end cursor before potentially showing dialog
            if wx.IsBusy():
                wx.EndBusyCursor()
            
            token_list = [(domain, token) for domain, token in tokens.items()]

            dlg = DNSChallengeDialog(self, token_list)

            if dlg.ShowModal() == wx.ID_OK:
                self.issue_certificate()
            dlg.Destroy()
        except Exception as e:
            if wx.IsBusy():
                wx.EndBusyCursor()
            self.report_error(e)

    def report_error(self, e):
        import traceback
        error_details = traceback.format_exc()
        
        dlg = wx.Dialog(self, title="Error Occurred", size=(500, 300))
        panel = wx.Panel(dlg)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(panel, label="An error occurred:"), 0, wx.ALL, 5)
        text_ctrl = wx.TextCtrl(panel, value=str(e), style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        
        copy_btn = wx.Button(panel, label="Copy Error Data")
        copy_btn.Bind(wx.EVT_BUTTON, lambda evt: self.copy_to_clipboard_generic(error_details, "Error Data"))
        sizer.Add(copy_btn, 0, wx.ALL | wx.CENTER, 5)
        
        panel.SetSizer(sizer)
        dlg.ShowModal()
        dlg.Destroy()
        
    def copy_to_clipboard_generic(self, text, label):
        clipboard = wx.Clipboard.Get()
        if clipboard.Open():
            data = wx.TextDataObject(text)
            clipboard.SetData(data)
            clipboard.Flush()
            clipboard.Close()
            wx.MessageBox(f"Copied {label} to clipboard!", "Success")

    def issue_certificate(self):
        wx.MessageBox("Requesting certificate...", "Info")
        cert = self.client.request_certificate()
        key = self.client.private_key
        
        dlg = IssuanceResultDialog(self, cert, key)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = NVACFrame()
    app.MainLoop()
