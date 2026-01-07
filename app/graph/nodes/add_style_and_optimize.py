from weasyprint import HTML
from app.graph.state import FileResult, State
import uuid
from pathlib import Path
from app.graph.chains.add_style_and_optimize import add_style_chain

TEMP_FILES_DIR = Path("temp_files")
TEMP_FILES_DIR.mkdir(exist_ok=True)

async def add_style_and_optimize(state: State) -> State:
  final_html_structure = state["html_structure"]
  
  result = await add_style_chain.ainvoke(
    {"final_html_structure": final_html_structure}
  )

  file_id = str(uuid.uuid4())
  pdf_filename = f"{file_id}.pdf"
  pdf_path = TEMP_FILES_DIR / pdf_filename
    
  HTML(string=result).write_pdf(str(pdf_path))
  file_size = pdf_path.stat().st_size

  pdf_result = FileResult(
        file_id=file_id,
        download_url=f"/download/{file_id}",
        filename="CV.pdf",
        size=file_size
    )
  
  return {
    "final_html": result,
    "pdf_result": pdf_result
    }
  