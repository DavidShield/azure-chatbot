# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

import openai
from flask import Flask, render_template, request
from base import Message, Prompt, Conversation
from flask_minify  import Minify

from apps import app

DEBUG = app.config['DEBUG'] 

MODEL_ENGINE = "text-davinci-003"
BOT_NAME = "AI"
USER_NAME = "HUMAN"
STOP = "<|endoftext|>"
INSTRUCTIONS = "You are a Microsoft Azure Expert. As we creating Always On availability group for SQL Server on Azure Virtual Machines, you are supposed to answer questions directly and append a real doc reference at the end if available."
EXAMPLE_CONVOS = [
    ["Human: How to choose the right vm size?",
     "AI: Review the following checklist for a brief overview of the VM size best practices that the rest of the article covers in greater detail:\nThe new Ebdsv5-series provides the highest I/O throughput-to-vCore ratio in Azure along with a memory-to-vCore ratio of 8. This series offers the best price-performance for SQL Server workloads on Azure VMs. Consider this series first for most SQL Server workloads.\nUse VM sizes with 4 or more vCPUs like the E4ds_v5 or higher.\nUse memory optimized virtual machine sizes for the best performance of SQL Server workloads.\nThe Edsv5 series, the M-, and the Mv2- series offer the optimal memory-to-vCore ratio required for OLTP workloads.\nThe M series VMs offer the highest memory-to-vCore ratio in Azure. Consider these VMs for mission critical and data warehouse workloads.\nLeverage Azure Marketplace images to deploy your SQL Server Virtual Machines as the SQL Server settings and storage options are configured for optimal performance.\nCollect the target workload's performance characteristics and use them to determine the appropriate VM size for your business.\nUse the Data Migration Assistant SKU recommendation tool to find the right VM size for your existing SQL Server workload.\nTo learn more, see the comprehensive VM size best practices https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/performance-guidelines-best-practices-vm-size?view=azuresql."
    ],
    ["Human: Why Azure Hybrid Benefit?",
     "AI: Save up to 85% over standard pay-as-you-go rate leveraging Windows Server and SQL Server licenses with Azure Hybrid Benefit.ii\nUse Azure Hybrid Benefit in Azure SQL platform as a service (PaaS) environments.\nApply to SQL Server 1 to 4 vCPUs exchange: For every 1 core of SQL Server Enterprise Edition, you get 4 vCPUs of SQL Managed Instance or Azure SQL Database general purpose and Hyperscale tiers, or 4 vCPUs of SQL Server Standard edition on Azure VMs.\nUse existing SQL licensing to adopt Azure Arc–enabled SQL Managed Instance.\nHelp meet compliance requirements with unlimited virtualization on Azure Dedicated Host and Azure VMWare Solution.\nGet 180 days of dual-use rights between on-premises and Azure. To see more details, please visit https://azure.microsoft.com/en-us/pricing/hybrid-benefit/#calculator"
    ]
]



if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

app.logger.info('DEBUG            = ' + str( DEBUG )                 )
app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
app.logger.info('ASSETS_ROOT      = ' + app.config['ASSETS_ROOT']    )


openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return getResponse(userText)


def getResponse(message):
    messages = [Message(user=USER_NAME, text=message)]
    try:
        prompt = Prompt(
            header=Message(
                "System", f"Instructions for {BOT_NAME}: {INSTRUCTIONS}"
            ),
            examples=f"\n{STOP}".join(str(item) for innerlist in EXAMPLE_CONVOS for item in innerlist),
            convo=Conversation(messages + [Message(BOT_NAME)]),
        )
        rendered = prompt.render()
        response = openai.Completion.create(
            engine=MODEL_ENGINE,
            prompt=rendered,
            temperature=0,
            top_p=1,
            max_tokens=512,
            stop=[STOP],
        )
        reply = response.choices[0].text.strip()
        if reply:
            return response
    except openai.error.InvalidRequestError as e:
        if "This model's maximum context length" in e.user_message:
            print(e)
            return "TOO LONG"
        else:
            print(e)
            return "INVALID REQUEST"
    except Exception as e:
        print(e)
        return "OTHER ERROR"

if __name__ == "__main__":
    app.run()
