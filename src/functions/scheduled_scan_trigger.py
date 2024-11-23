# 2. Next, create: src/functions/scheduled_scan_trigger.py

import azure.functions as func
import logging
from ..scanners.scheduled_scanner import ScheduledScanManager

async def main(mytimer: func.TimerRequest) -> None:
    logging.info('Scheduled scan trigger function started')
    
    scan_manager = ScheduledScanManager()
    
    # Define scan schedule
    daily_scans = ['vulnerability', 'container']
    weekly_scans = ['compliance', 'sast']
    
    try:
        # Run daily scans
        for scan_type in daily_scans:
            await scan_manager.run_scheduled_scan(scan_type)
            
        # Run weekly scans on Sunday
        if datetime.now().weekday() == 6:  # Sunday
            for scan_type in weekly_scans:
                await scan_manager.run_scheduled_scan(scan_type)
                
    except Exception as e:
        logging.error(f"Error in scheduled scan: {str(e)}")
        raise