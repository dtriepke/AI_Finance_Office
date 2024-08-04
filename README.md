



# AI Finance Office (Autogen agentic project)

Welcome to the AI Finance Office project! This project aims to revolutionize the finance back-office by leveraging AI agent crews to automate and streamline various financial processes. Our goal is to create an entirely AI-driven finance office that enhances efficiency, reduces errors, and provides seamless financial management.

*Note: all remining api keys in the code are already disabled.*
## Overview

In the initial phase of this project, we have developed two key AI agent crews:

1. **Chart of Accounts (CoA) Crew**: 
    * Using LlamaIndex, Deep Lake Index and auogen  
    * Follow: `1. CoA_smart_agent_with_autogen_and_deep_lake.ipynb`
2. **Invoice Processing Crew**: 
    * Using LlamaIndex, LlamaParse and autogen  
    * Follow: `2. Invoice_processing_smart_agent_wiht_llamaparse_and_autogen.ipynb`



## Chart of Accounts (CoA) Crew with Deep Lake, LlamaIndex and auogen

Follow: `1. CoA_smart_agent_with_autogen_and_deep_lake.ipynb`

The CoA Crew is responsible for maintaining the Chart of Accounts, ensuring that all accounts are accurately categorized and up-to-date. This crew is equipped with advanced features, including:

- **IFRS Knowledge:** The crew has access to International Financial Reporting Standards (IFRS) knowledge, ensuring compliance with global accounting standards.
- **Internet Search:** The crew can perform internet searches to fetch the latest updates and information relevant to accounting practices and standards.

![alt text](pics/image.png)

## Invoice Processing Crew with LlamaParse, LlamaIndex and autogen

Follow: `2. Invoice_processing_smart_agent_wiht_llamaparse_and_autogen.ipynb`

**invoice_processing_agent:**  


The Invoice Processing Crew automates the handling of invoices, from reading and interpreting invoice data to verifying and matching it with corresponding Purchase Orders. Key capabilities of this crew include:

- **Invoice Reading:** Automatically reads and extracts information from invoices.
- **Purchase Order Matching:** Matches invoice data with the relevant Purchase Orders for validation.
- **Bank Account Verification:** Checks the associated bank account details to ensure accuracy and consistency.

**The crew:**  
  invoice_extraction_agent: Reads pdf invoice and extracts all information.   
  po_extraction_agent: Reads purchase orders form a SQL db given a vendor name.   
  ba_extraction_agent: Reads bank account balance information.  
  po_matching_agent: Verifies invoice with the PO and creates a report.   
  review_agent: reviews reports  
  logger: writes python code  


**Result Report generated from crew for 1 invoice:**  
The obejctive of the run was to to test the behaviour for:   
- inconsistent tax amount wiht PO database: -> detected 
- a to low bank balance to pay the invoice: -> detected 

```text
Revised Invoice Verification Report:

Summary of Findings:
- Invoice Number: 97159829
- Creditor Name: Bradley-Andrade
- Description of Goods or Service: 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537
- Invoice Date: 09/18/2015
- Purchase Order Date: 09/18/2015
- Overall Status: Yellow
- Likelihood of Fraud: 30% risk (based on discrepancies in tax amounts and missing purchase order number)
- Bank Account Balance Coverage: No (current balance is $200, invoice net amount is $889.2)
- Action Items: Contact creditor to resolve tax discrepancy and missing purchase order number; review internal controls.

Detailed Report:
- The invoice and purchase order dates align, both being on 09/18/2015.
- Payment terms are not specified in the provided data for both the invoice and the purchase order.
- The currency is not mentioned in the provided data; it is assumed to be the local currency of the company.
- The bank account balance date is 06/23/2024, indicating the financial status at the time of the report.
- The likelihood of fraud is assessed at 30% risk due to the tax amount discrepancy and the absence of a purchase order number on the invoice. 
  The methodology for this assessment should be reviewed and clarified.
- The tax amounts are inconsistent, with the invoice stating $88.92 and the purchase order stating $10.00.
- The purchase order number is missing from the invoice; the corresponding number is 333333.
- The line item net amount, total net amount, and gross amount match between the invoice and the purchase order.
- The invoice line item description and amount match the purchase order, with a correction from "2 unite" to "2 units."

Formatting and Consistency:
- The report has been formatted for consistency and clarity.

Next Steps:
- Contact Bradley-Andrade to address the tax amount discrepancy and to add the missing purchase order number to the invoice.
- Review internal controls to ensure purchase order numbers are included on all invoices and that tax amounts are correctly calculated and reported.
- Assess the company's current financial position and take necessary actions to ensure sufficient funds are available to cover upcoming invoices.
```


**Purchase order matching agent**
```Python
system_message="""Purchase order matching agent. 
    
    You receive invoice data from 'invoice_extraction_agent' and you receive purchase order data from 'po_extraction_agent'.
    You receive bank balance data from 'ba_extraction_agent'

    Vefify that the invoices details below matches the Purchase Order (PO): 
        line_item_net_amount, 
        total_net_amount, 
        gross_amount, 
        tax_amounts, 
        discounts, 
        creditor_name, 
        description_of_goods_or_service, 
        line_items, 
        line_item_amount
    
    Creates a verification report for the PO-invoice match for a CEO:   
    - Overall Status: green, yellow or red
    - Likelohhod of fraud: number between 1 and 100 that indicates the probability of of fraud as well as the reasonong
    - *Summary*: Summarise the key points.
    - *Red Flags*: Summarise the red flags of missing invoice details in the purchase order  
    - *Check Calculations:* Ensure that all calculations on the invoice, including unit prices, quantities, discounts, and totals, are accurat 
    - Bank account balance coverage: answer can the invoice net amount total be paid with the current bank account balance? 

    The user cannot provide any other feedback or perform any other action. The user can't modify your report. So do not suggest incomplete reports which requires users to modify!

    Here is an example: 
    
        Revised Invoice Verification Report:

        Summary of Findings:
        - Invoice Number: 97159829
        - Creditor Name: Bradley-Andrade
        - Description of Goods or Service: 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537
        - Invoice Date: 09/18/2015
        - Purchase Order Date: 09/18/2015
        - Overall Status: Yellow
        - Likelihood of Fraud: 30% risk (based on discrepancies in tax amounts and missing purchase order number)
        - Bank Account Balance Coverage: No (current balance is $200, invoice net amount is $889.2)
        - Action Items: Contact creditor to resolve tax discrepancy and missing purchase order number; review internal controls.

        Detailed Report:
        - The invoice and purchase order dates align, both being on 09/18/2015.
        - Payment terms are not specified in the provided data for both the invoice and the purchase order.
        - The currency is not mentioned in the provided data; it is assumed to be the local currency of the company.
        - The bank account balance date is 06/23/2024, indicating the financial status at the time of the report.
        - The likelihood of fraud is assessed at 30% risk due to the tax amount discrepancy and the absence of a purchase order number on the invoice. The methodology for this assessment should be reviewed and clarified.
        - The tax amounts are inconsistent, with the invoice stating $88.92 and the purchase order stating $10.00.
        - The purchase order number is missing from the invoice; the corresponding number is 333333.
        - The line item net amount, total net amount, and gross amount match between the invoice and the purchase order.
        - The invoice line item description and amount match the purchase order, with a correction from "2 unite" to "2 units."

        Formatting and Consistency:
        - The report has been formatted for consistency and clarity.

        Next Steps:
        - Contact Bradley-Andrade to address the tax amount discrepancy and to add the missing purchase order number to the invoice.
        - Review internal controls to ensure purchase order numbers are included on all invoices and that tax amounts are correctly calculated and reported.
        - Assess the company's current financial position and take necessary actions to ensure sufficient funds are available to cover upcoming invoices.
            

"""

```

**Reviewer**  
```python
   system_message="""Reviewer

After the po_matching_agent writes the a report, it's passed to you. Your primary role is to ensure the report's quality and efficiency. 
You are responsible for review the report form not the report itself. Provide feedback to the po_matching_agent.
Iterate until po_matching_agent writes report that is perfect. You decide that the report is successful or not.

""" 

description = "You review invoice verification report from the po_macthing_agent and execute code to store the report. When you forward the python code say 'TERMINATE'"

```
**Logger**  
```python
system_message="""Logger and Python Code Developer

Recieve the Report from Reviewer and write a python code to store the report as *.txt file with the invoive number as file name with report_directory = "./reports"  

In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself. 
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. 
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. 
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. Include no more than one code block in a response. 
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. 
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. 
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. 
Please conclude with "TERMINATE" once you have successfully answered the user's instruction or question.

""",
description = "Write python code to store report as txt files."

```
**Group Chat Manager**  
```python
system_message = """
# Overview:

invoice_extraction_agent: processes the pdf invoice form given a file path and forwards the extracted data to both po_extraction_agent and po_matching_agent. 

po_extraction_agent: fetches purchase orders for that invoice given a vendor name from the invoice data received from invoice_extraction_agent.

ba_extraction_agent: Recieves bank account balance data and reports to the review agent po_matching_agent to verify the if invoice is covered by the bank account.

po_matching_agent: Recieves invoice data from invoice_extraction_agent,  purchase order data from po_extraction_agent and bank balance from ba_extraction_agent to verify the invoice. It forwards a report to the review agent.

review_agent: Recieves a report from the po_matching_agent. If it finds any report form issues, Reviewer provides detailed feedback with instructions to the po_matching_agent. 
This process will iterate until the report is perfect. REVIEWER CAN PROVIDE FEEBACK TO po_matching_agent.

logger: is skilled at executing python code to store the report.

init: excecutes the python code generated from logger to store the report.


"""
description = """You are a manager of a team of invoice processing experts. 
  invoice_extraction_agent: Reads pdf invoice and extracts all information. 
  po_extraction_agent: Reads purchase orders form a SQL db given a vendor name. 
  ba_extraction_agent: Reads bank account balance information.
  po_matching_agent: Verifies invoice with the PO and creates a report. 
  review_agent: reviews reports
  logger: writes python code"""


```


## Getting Started

To get started with the AI Finance Office project, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/dtriepke/AI_Finance_Office.git 

2. **Play with the crews:**  
 
- Open `CoA_smart_agent_2.ipynb`
- Open `Invoice_smart_agent_1.ipynb`



## Examples Prints: 


init (to chat_manager):

Process the invoice from the path: .\data\invoices\output_0.pdf

--------------------------------------------------------------------------------

Next speaker: invoice_extraction_agent

invoice_extraction_agent (to chat_manager):

***** Suggested function call: invoice_reader *****
Arguments: 
{"path_to_invoice":".\\data\\invoices\\output_0.pdf"}
***************************************************

--------------------------------------------------------------------------------

Next speaker: invoice_user


>>>>>>>> EXECUTING FUNCTION invoice_reader...
Started parsing the file under job_id cac11eca-4202-47da-93ae-0fbfd2fd2982
Function call: Invoice with args: {"date":"09/18/2015","invoice_number":"97159829","net_amount":889.20,"gross_amount":978.12,"tax_amounts":88.92,"seller_name":"Bradley-Andrade","creditor_name":"Bradley-Andrade","description_of_goods_or_service":"12\" Marble Lapis Inlay Chess Table Top With 2\" Pieces & 15\" Wooden Stand W537","line_items":[{"description":"12\" Marble Lapis Inlay Chess Table Top With 2\" Pieces & 15\" Wooden Stand W537","quantity":2,"unit_price":444.60,"total_price":889.20}]}
invoice_user (to chat_manager):

***** Response from calling function (invoice_reader) *****
date='09/18/2015' due_date=None invoice_number='97159829' net_amount=889.2 gross_amount=978.12 tax_amounts=88.92 discounts=None seller_name='Bradley-Andrade' creditor_name='Bradley-Andrade' purchase_order_number=None payment_terms=None currency=None description_of_goods_or_service='12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537' line_items=[LineItem(description='12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537', quantity=2, unit_price=444.6, total_price=889.2)]
***********************************************************

--------------------------------------------------------------------------------

Next speaker: po_extraction_agent


>>>>>>>> USING AUTO REPLY...
po_extraction_agent (to chat_manager):

***** Suggested function call: purchase_order_reader *****
Arguments: 
{"po_request":"Bradley-Andrade"}
**********************************************************

--------------------------------------------------------------------------------

Next speaker: po_user


>>>>>>>> EXECUTING FUNCTION purchase_order_reader...
Function call: PurchaseOrder with args: {"date":"09/18/2015","net_amount":889.2,"gross_amount":978.12,"tax_amounts":10,"discounts":null,"seller_name":"Bradley-Andrade","creditor_name":"Bradley-Andrade","purchase_order_number":"333333","payment_terms":null,"currency":null,"description_of_goods_or_service":"12\" Marble Lapis Inlay Chess Table Top With 2\" Pieces & 15\" Wooden Stand W537","line_items":[{"description":"2 unite 12\" Marble Lapis Inlay Chess Table Top With 2\" Pieces & 15\" Wooden Stand W537 @ 444.6 each","quantity":2,"unit_price":444.6,"total_price":889.2}]}
po_user (to chat_manager):

***** Response from calling function (purchase_order_reader) *****
[PurchaseOrder(date='09/18/2015', net_amount=889.2, gross_amount=978.12, tax_amounts=10.0, discounts=None, seller_name='Bradley-Andrade', creditor_name='Bradley-Andrade', purchase_order_number='333333', payment_terms=None, currency=None, description_of_goods_or_service='12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537', line_items=[LineItem(description='2 unite 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537 @ 444.6 each', quantity=2, unit_price=444.6, total_price=889.2)])]
******************************************************************

--------------------------------------------------------------------------------

Next speaker: po_matching_agent

po_matching_agent (to chat_manager):

To proceed with the verification, I need to know the current bank account balance. Could you please provide the bank balance data from the 'ba_extraction_agent'?

--------------------------------------------------------------------------------

Next speaker: ba_extraction_agent


>>>>>>>> USING AUTO REPLY...
ba_extraction_agent (to chat_manager):

***** Suggested function call: bank_account_reader *****
Arguments: 
{"bank_account_request":"current balance"}
********************************************************

--------------------------------------------------------------------------------

Next speaker: ba_user


>>>>>>>> EXECUTING FUNCTION bank_account_reader...
ba_user (to chat_manager):

***** Response from calling function (bank_account_reader) *****
date='2024-06-23 17:45:51.055355' net_amount=200.0
****************************************************************

--------------------------------------------------------------------------------

Next speaker: po_matching_agent

po_matching_agent (to chat_manager):

Invoice Verification Report:

Summary:
- Invoice Number: 97159829
- Creditor Name: Bradley-Andrade
- Description of Goods or Service: 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537
- Overall Status: yellow
- Likelihood of fraud:
    - Score: 30% risk
    - Reasoning: The tax amount on the invoice does not match the expected tax amount from the purchase order, and the purchase order number is missing from the invoice. These discrepancies could indicate a potential issue with the invoice's validity.
- Bank Account Balance Coverage: No, the current bank account balance is $200, which is below the invoice net amount total of $889.2.

Red Flags:
- Tax Amounts: The invoice specifies a tax amount of $88.92, whereas the purchase order indicates a tax amount of $10.00. This significant discrepancy needs to be resolved.
- Purchase Order Number: The invoice does not reference a purchase order number, which is typically required for matching and verification purposes. The corresponding purchase order number is 333333.

Check Calculations:
- Line Item Net Amount: Matches the purchase order (2 units at $444.6 each, total $889.2).
- Total Net Amount: Matches the purchase order ($889.2).
- Gross Amount: Matches the purchase order ($978.12).
- Line Item Amount: The invoice line item amount matches the purchase order line item amount ($889.2).

All other calculations on the invoice, including unit prices and quantities, are accurate and match the purchase order details. However, the discrepancy in the tax amount and the missing purchase order number on the invoice are areas of concern that should be addressed. Additionally, the current bank account balance is insufficient to cover the invoice amount, which could lead to payment issues.

--------------------------------------------------------------------------------

Next speaker: reviewer

reviewer (to chat_manager):

The report form is well-structured and includes essential details for invoice verification. However, there are a few areas that need to be addressed to ensure the report's quality and efficiency:

1. **Invoice Date and Purchase Order Date**: The report should mention the dates of both the invoice and the purchase order to confirm they align and are within acceptable terms.

2. **Payment Terms**: If available, the report should include payment terms from both the invoice and the purchase order to ensure they match and to determine the payment due date.

3. **Currency**: The currency should be specified to avoid any confusion, especially if the company operates internationally.

4. **Bank Account Balance Date**: The report should mention the date of the bank account balance to provide context for the financial status.

5. **Likelihood of Fraud**: The report should clarify how the 30% risk score was determined. Is there a specific methodology or set of criteria used to assess the risk of fraud?

6. **Action Items**: The report should suggest next steps or action items, such as contacting the creditor to resolve discrepancies or reviewing internal controls to prevent future mismatches.

7. **Formatting**: Ensure that the report is formatted consistently. For example, "2 unite" in the purchase order line item description should be corrected to "2 units."

8. **Summary of Findings**: It would be beneficial to have a concise summary of findings at the beginning of the report for quick reference.

Please revise the report to include these details and corrections.

--------------------------------------------------------------------------------

Next speaker: logger

logger (to chat_manager):

Revised Invoice Verification Report:

Summary of Findings:
- Invoice Number: 97159829
- Creditor Name: Bradley-Andrade
- Description of Goods or Service: 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537
- Invoice Date: 09/18/2015
- Purchase Order Date: 09/18/2015
- Overall Status: Yellow
- Likelihood of Fraud: 30% risk (based on discrepancies in tax amounts and missing purchase order number)
- Bank Account Balance Coverage: No (current balance is $200, invoice net amount is $889.2)
- Action Items: Contact creditor to resolve tax discrepancy and missing purchase order number; review internal controls.

Detailed Report:
- The invoice and purchase order dates align, both being on 09/18/2015.
- Payment terms are not specified in the provided data for both the invoice and the purchase order.
- The currency is not mentioned in the provided data; it is assumed to be the local currency of the company.
- The bank account balance date is 06/23/2024, indicating the financial status at the time of the report.
- The likelihood of fraud is assessed at 30% risk due to the tax amount discrepancy and the absence of a purchase order number on the invoice. The methodology for this assessment should be reviewed and clarified.
- The tax amounts are inconsistent, with the invoice stating $88.92 and the purchase order stating $10.00.
- The purchase order number is missing from the invoice; the corresponding number is 333333.
- The line item net amount, total net amount, and gross amount match between the invoice and the purchase order.
- The invoice line item description and amount match the purchase order, with a correction from "2 unite" to "2 units."

Formatting and Consistency:
- The report has been formatted for consistency and clarity.

Next Steps:
- Contact Bradley-Andrade to address the tax amount discrepancy and to add the missing purchase order number to the invoice.
- Review internal controls to ensure purchase order numbers are included on all invoices and that tax amounts are correctly calculated and reported.
- Assess the company's current financial position and take necessary actions to ensure sufficient funds are available to cover upcoming invoices.

Please review the revised report and let me know if there are any further changes required.

--------------------------------------------------------------------------------

Next speaker: logger

logger (to chat_manager):

To store the revised report as a text file with the invoice number as the filename, you can use the following Python code:

```python
import os

# Report content
report_content = """
Revised Invoice Verification Report:

Summary of Findings:
- Invoice Number: 97159829
- Creditor Name: Bradley-Andrade
- Description of Goods or Service: 12" Marble Lapis Inlay Chess Table Top With 2" Pieces & 15" Wooden Stand W537
- Invoice Date: 09/18/2015
- Purchase Order Date: 09/18/2015
- Overall Status: Yellow
- Likelihood of Fraud: 30% risk (based on discrepancies in tax amounts and missing purchase order number)
- Bank Account Balance Coverage: No (current balance is $200, invoice net amount is $889.2)
- Action Items: Contact creditor to resolve tax discrepancy and missing purchase order number; review internal controls.

Detailed Report:
- The invoice and purchase order dates align, both being on 09/18/2015.
- Payment terms are not specified in the provided data for both the invoice and the purchase order.
- The currency is not mentioned in the provided data; it is assumed to be the local currency of the company.
- The bank account balance date is 06/23/2024, indicating the financial status at the time of the report.
- The likelihood of fraud is assessed at 30% risk due to the tax amount discrepancy and the absence of a purchase order number on the invoice. The methodology for this assessment should be reviewed and clarified.
- The tax amounts are inconsistent, with the invoice stating $88.92 and the purchase order stating $10.00.
- The purchase order number is missing from the invoice; the corresponding number is 333333.
- The line item net amount, total net amount, and gross amount match between the invoice and the purchase order.
- The invoice line item description and amount match the purchase order, with a correction from "2 unite" to "2 units."

Formatting and Consistency:
- The report has been formatted for consistency and clarity.

Next Steps:
- Contact Bradley-Andrade to address the tax amount discrepancy and to add the missing purchase order number to the invoice.
- Review internal controls to ensure purchase order numbers are included on all invoices and that tax amounts are correctly calculated and reported.
- Assess the company's current financial position and take necessary actions to ensure sufficient funds are available to cover upcoming invoices.
"""

# Directory to store the report
report_directory = "./reports"

# Invoice number to be used as the file name
invoice_number = "97159829"

# Function to save the report
def save_report(report, directory, filename):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Attempt to save the file
    suffix = 0
    while True:
        try:
            # Add a suffix if necessary
            file_name_with_suffix = f"{filename}{'' if suffix == 0 else '_' + str(suffix)}.txt"
            file_path = os.path.join(directory, file_name_with_suffix)
            
            # Write the report to the file
            with open(file_path, 'w') as file:
                file.write(report)
            print(f"Report saved successfully as {file_path}")
            break
        except OSError as e:
            print(f"Error saving report: {e}")
            suffix += 1  # Increment suffix and try again

# Save the report
save_report(report_content, report_directory, invoice_number)
```

This code will create a directory called "reports" if it doesn't exist and save the report as a text file with the invoice number as the filename. If there is an error while saving, it will add a suffix to the filename and try again.

--------------------------------------------------------------------------------

Next speaker: invoice_user


>>>>>>>> EXECUTING CODE BLOCK 0 (inferred language is python)...
invoice_user (to chat_manager):

exitcode: 0 (execution succeeded)
Code output: 
Report saved successfully as ./reports\97159829.txt


--------------------------------------------------------------------------------

Next speaker: reviewer

reviewer (to chat_manager):

The revised report has been successfully saved as a text file named "97159829.txt" in the "./reports" directory. If you require any further assistance or need additional modifications to the report, please let me know.

--------------------------------------------------------------------------------

