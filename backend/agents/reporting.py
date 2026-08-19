from __future__ import annotations
from typing import Any
from tools.markdown import MarkdownReportWriter
class ReportingAgent:
    def __init__(self): self.writer=MarkdownReportWriter()
    def pre(self,state:dict[str,Any])->dict[str,Any]:return self.writer.create(state,'pre-upgrade-report')
    def post(self,state:dict[str,Any])->dict[str,Any]:return self.writer.create(state,'post-upgrade-report')
