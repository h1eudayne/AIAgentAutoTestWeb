# Screenshot Diff - Visual regression testing
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import json


class ScreenshotDiff:
    """
    Screenshot Diff - Visual regression testing
    So sánh screenshots để phát hiện thay đổi UI
    """
    
    def __init__(self, baseline_dir: str = "screenshots/baseline",
                 current_dir: str = "screenshots/current",
                 diff_dir: str = "screenshots/diff"):
        self.baseline_dir = Path(baseline_dir)
        self.current_dir = Path(current_dir)
        self.diff_dir = Path(diff_dir)
        
        # Create directories
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.diff_dir.mkdir(parents=True, exist_ok=True)
        
        self.comparison_results = []
        self.threshold = 0.1  # Default threshold
    
    def capture_baseline(self, driver, name: str) -> str:
        """
        Capture baseline screenshot
        """
        filepath = self.baseline_dir / f"{name}.png"
        driver.save_screenshot(str(filepath))
        print(f"📸 Baseline captured: {name}")
        return str(filepath)
    
    def capture_current(self, driver, name: str) -> str:
        """
        Capture current screenshot
        """
        filepath = self.current_dir / f"{name}.png"
        driver.save_screenshot(str(filepath))
        return str(filepath)
    
    def compare(self, name: str, threshold: Optional[float] = None) -> Dict:
        """
        Compare baseline vs current screenshot
        
        Args:
            name: Screenshot name
            threshold: Pixel difference threshold (0-1), default 0.1
        
        Returns:
            Dict with comparison results
        """
        if threshold is None:
            threshold = self.threshold
        
        baseline_path = self.baseline_dir / f"{name}.png"
        current_path = self.current_dir / f"{name}.png"
        diff_path = self.diff_dir / f"{name}_diff.png"
        
        # Check if files exist
        if not baseline_path.exists():
            return {
                "name": name,
                "status": "no_baseline",
                "message": "Baseline screenshot not found",
                "mismatch_pixels": 0,
                "mismatch_percentage": 0
            }
        
        if not current_path.exists():
            return {
                "name": name,
                "status": "no_current",
                "message": "Current screenshot not found",
                "mismatch_pixels": 0,
                "mismatch_percentage": 0
            }
        
        try:
            # Load images
            img_baseline = Image.open(baseline_path).convert('RGBA')
            img_current = Image.open(current_path).convert('RGBA')
            
            # Check if dimensions match
            if img_baseline.size != img_current.size:
                # Resize current to match baseline
                img_current = img_current.resize(img_baseline.size, Image.LANCZOS)
            
            # Create diff image
            img_diff = Image.new("RGBA", img_baseline.size)
            
            # Compare
            mismatch_pixels = pixelmatch(
                img_baseline, 
                img_current, 
                img_diff,
                threshold=threshold,
                includeAA=True
            )
            
            # Calculate percentage
            total_pixels = img_baseline.size[0] * img_baseline.size[1]
            mismatch_percentage = (mismatch_pixels / total_pixels) * 100
            
            # Save diff image
            img_diff.save(diff_path)
            
            # Determine status
            if mismatch_pixels == 0:
                status = "identical"
            elif mismatch_percentage < 1:
                status = "minor_diff"
            elif mismatch_percentage < 5:
                status = "moderate_diff"
            else:
                status = "major_diff"
            
            result = {
                "name": name,
                "status": status,
                "mismatch_pixels": mismatch_pixels,
                "total_pixels": total_pixels,
                "mismatch_percentage": round(mismatch_percentage, 2),
                "threshold": threshold,
                "baseline_path": str(baseline_path),
                "current_path": str(current_path),
                "diff_path": str(diff_path),
                "timestamp": datetime.now().isoformat()
            }
            
            self.comparison_results.append(result)
            
            # Print result
            self._print_comparison_result(result)
            
            return result
            
        except Exception as e:
            result = {
                "name": name,
                "status": "error",
                "message": str(e),
                "mismatch_pixels": 0,
                "mismatch_percentage": 0
            }
            self.comparison_results.append(result)
            return result
    
    def _print_comparison_result(self, result: Dict):
        """Print comparison result"""
        from colorama import Fore, Style
        
        name = result["name"]
        status = result["status"]
        mismatch_pct = result.get("mismatch_percentage", 0)
        
        if status == "identical":
            print(f"  {Fore.GREEN}✓ {name}: Identical{Style.RESET_ALL}")
        elif status == "minor_diff":
            print(f"  {Fore.YELLOW}⚠ {name}: Minor diff ({mismatch_pct}%){Style.RESET_ALL}")
        elif status == "moderate_diff":
            print(f"  {Fore.YELLOW}⚠ {name}: Moderate diff ({mismatch_pct}%){Style.RESET_ALL}")
        elif status == "major_diff":
            print(f"  {Fore.RED}✗ {name}: Major diff ({mismatch_pct}%){Style.RESET_ALL}")
        elif status == "no_baseline":
            print(f"  {Fore.CYAN}ℹ {name}: No baseline (creating){Style.RESET_ALL}")
        elif status == "error":
            print(f"  {Fore.RED}✗ {name}: Error - {result.get('message')}{Style.RESET_ALL}")
    
    def compare_multiple(self, names: list, threshold: Optional[float] = None) -> list:
        """
        Compare multiple screenshots
        """
        results = []
        for name in names:
            result = self.compare(name, threshold)
            results.append(result)
        return results
    
    def get_summary(self) -> Dict:
        """Get comparison summary"""
        if not self.comparison_results:
            return {
                "total": 0,
                "identical": 0,
                "minor_diff": 0,
                "moderate_diff": 0,
                "major_diff": 0,
                "errors": 0
            }
        
        summary = {
            "total": len(self.comparison_results),
            "identical": 0,
            "minor_diff": 0,
            "moderate_diff": 0,
            "major_diff": 0,
            "no_baseline": 0,
            "errors": 0
        }
        
        for result in self.comparison_results:
            status = result["status"]
            if status in summary:
                summary[status] += 1
        
        return summary
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """Save comparison report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_diff_report_{timestamp}.json"
        
        filepath = self.diff_dir / filename
        
        report = {
            "summary": self.get_summary(),
            "comparisons": self.comparison_results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Screenshot diff report saved: {filepath}")
        return str(filepath)
    
    def print_summary(self):
        """Print summary to console"""
        from colorama import Fore, Style
        
        summary = self.get_summary()
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📸 SCREENSHOT COMPARISON SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"Total Comparisons: {summary['total']}")
        print(f"{Fore.GREEN}✓ Identical: {summary['identical']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Minor Diff: {summary['minor_diff']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Moderate Diff: {summary['moderate_diff']}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Major Diff: {summary['major_diff']}{Style.RESET_ALL}")
        
        if summary.get('no_baseline', 0) > 0:
            print(f"{Fore.CYAN}ℹ No Baseline: {summary['no_baseline']}{Style.RESET_ALL}")
        
        if summary.get('errors', 0) > 0:
            print(f"{Fore.RED}✗ Errors: {summary['errors']}{Style.RESET_ALL}")
        
        # Show major diffs
        major_diffs = [r for r in self.comparison_results if r["status"] == "major_diff"]
        if major_diffs:
            print(f"\n{Fore.RED}Major Differences:{Style.RESET_ALL}")
            for diff in major_diffs[:5]:  # Show first 5
                print(f"  • {diff['name']}: {diff['mismatch_percentage']}% different")
        
        print()
    
    def update_baseline(self, name: str):
        """
        Update baseline with current screenshot
        """
        current_path = self.current_dir / f"{name}.png"
        baseline_path = self.baseline_dir / f"{name}.png"
        
        if current_path.exists():
            import shutil
            shutil.copy(current_path, baseline_path)
            print(f"✓ Baseline updated: {name}")
        else:
            print(f"✗ Current screenshot not found: {name}")
    
    def update_all_baselines(self):
        """Update all baselines with current screenshots"""
        for current_file in self.current_dir.glob("*.png"):
            name = current_file.stem
            self.update_baseline(name)
    
    def clear_current(self):
        """Clear current screenshots"""
        for file in self.current_dir.glob("*.png"):
            file.unlink()
        print("✓ Current screenshots cleared")
    
    def clear_diff(self):
        """Clear diff screenshots"""
        for file in self.diff_dir.glob("*.png"):
            file.unlink()
        print("✓ Diff screenshots cleared")
