tax_tag_names = ["-fi_307"]
tax_ids = env["account.account.tag"].search([("name", "in", tax_tag_names)])
journal_item_label = "Put some text here"
journal_items = env["account.move.line"].search([("label", "=", journal_item_label)])