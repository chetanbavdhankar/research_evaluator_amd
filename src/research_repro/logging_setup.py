import logging
import os
from pathlib import Path

# Formatter that includes phase and agent (which can be passed via extra)
class ReproFormatter(logging.Formatter):
    def format(self, record):
        # Provide defaults for phase and agent if not present in the record
        if not hasattr(record, 'phase'):
            record.phase = 'global'
        if not hasattr(record, 'agent'):
            record.agent = 'system'
        return super().format(record)

def setup_global_logger(run_dir: str):
    log_dir = Path(run_dir) / "artifacts" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    pipeline_log = log_dir / "pipeline.log"
    
    root_logger = logging.getLogger("research_repro")
    root_logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if called multiple times
    root_logger.handlers = []
    
    file_handler = logging.FileHandler(pipeline_log)
    formatter = ReproFormatter("%(asctime)s %(levelname)s %(phase)s %(agent)s %(message)s")
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

def get_phase_logger(run_dir: str, phase_number: int, agent_name: str = "system") -> logging.LoggerAdapter:
    log_dir = Path(run_dir) / "artifacts" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    phase_log = log_dir / f"phase{phase_number}.log"
    
    logger = logging.getLogger(f"research_repro.phase{phase_number}")
    logger.setLevel(logging.DEBUG) # Per spec: DEBUG level captures full prompts/responses
    
    # Only add handler if it hasn't been added
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(phase_log.resolve()) for h in logger.handlers):
        file_handler = logging.FileHandler(phase_log)
        formatter = ReproFormatter("%(asctime)s %(levelname)s %(phase)s %(agent)s %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    # Return an adapter that automatically injects phase and agent context
    return logging.LoggerAdapter(logger, {"phase": f"Phase{phase_number}", "agent": agent_name})
