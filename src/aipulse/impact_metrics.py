"""Impact metrics: analyze entity influence and topic momentum over time.

Tracks companies, models, researchers gaining or losing prominence by
normalizing mention frequency and trend direction across date ranges.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class EntityImpact:
    """Tracks entity influence metrics."""
        entity: str
            score: float
                mentions: int
                    trend: str  # 'rising', 'stable', 'falling'


                    def impact_window(entities_by_date: dict, start: str, end: str) -> list:
                        """Calculate impact scores across date ranges.

                                Args:
                                        entities_by_date: {date_str: [entities]}
                                                start: Start date YYYY-MM-DD
                                                        end: End date YYYY-MM-DD

                                                                    Returns:
                                                                            List of EntityImpact objects sorted by score descending.
                                                                                """
                                                                                    start_dt = datetime.strptime(start, '%Y-%m-%d')
                                                                                        end_dt = datetime.strptime(end, '%Y-%m-%d')

                                                                                                counts = defaultdict(int)
                                                                                                    for date_str in entities_by_date:
                                                                                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                                                                                    if start_dt <= date_obj <= end_dt:
                                                                                                                                for entity in entities_by_date[date_str]:
                                                                                                                                                counts[entity] += 1
                                                                                                                                                    
                                                                                                                                                        max_count = max(counts.values()) if counts else 1
                                                                                                                                                            impacts = []
                                                                                                                                                                for entity, count in counts.items():
                                                                                                                                                                        normalized = (count / max_count) * 100
                                                                                                                                                                                impacts.append(EntityImpact(entity, normalized, count, 'stable'))
                                                                                                                                                                                    
                                                                                                                                                                                        return sorted(impacts, key=lambda x: x.score, reverse=True)
                                                                                                                                                                                        
                                                                                                                                                                                        
                                                                                                                                                                                        def compare_impact(earlier: list, later: list) -> list:
                                                                                                                                                                                            """Rank entities by trajectory comparing two periods.
                                                                                                                                                                                                
                                                                                                                                                                                                    Returns:
                                                                                                                                                                                                            List of entities with trajectory analysis, sorted by rise first.
                                                                                                                                                                                                                """
                                                                                                                                                                                                                    earlier_dict = {e.entity: e.score for e in earlier}
                                                                                                                                                                                                                        later_dict = {e.entity: e.score for e in later}
                                                                                                                                                                                                                            
                                                                                                                                                                                                                                results = []
                                                                                                                                                                                                                                    all_entities = set(earlier_dict.keys()) | set(later_dict.keys())
                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                            for entity in all_entities:
                                                                                                                                                                                                                                                    old_score = earlier_dict.get(entity, 0)
                                                                                                                                                                                                                                                            new_score = later_dict.get(entity, 0)
                                                                                                                                                                                                                                                                    change = new_score - old_score
                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                    if change > 10:
                                                                                                                                                                                                                                                                                                trend = 'rising'
                                                                                                                                                                                                                                                                                                        elif change < -10:
                                                                                                                                                                                                                                                                                                                    trend = 'falling'
                                                                                                                                                                                                                                                                                                                            else:
                                                                                                                                                                                                                                                                                                                                        trend = 'stable'
                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                        results.append(EntityImpact(entity, new_score, int(new_score), trend))
                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                return sorted(results, key=lambda x: x.score, reverse=True)
                                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                if __name__ == "__main__":
                                                                                                                                                                                                                                                                                                                                                                    test_data = {
                                                                                                                                                                                                                                                                                                                                                                            '2026-11-01': ['OpenAI', 'NVIDIA', 'Anthropic'],
                                                                                                                                                                                                                                                                                                                                                                                    '2026-11-02': ['DeepSeek', 'xAI', 'OpenAI', 'NVIDIA'],
                                                                                                                                                                                                                                                                                                                                                                                            '2026-11-03': ['NVIDIA', 'Anthropic', 'OpenAI'],
                                                                                                                                                                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                        window = impact_window(test_data, '2026-11-01', '2026-11-03')
                                                                                                                                                                                                                                                                                                                                                                                                            print("Entity Impact (Nov 1-3):")
                                                                                                                                                                                                                                                                                                                                                                                                                for e in window:
                                                                                                                                                                                                                                                                                                                                                                                                                        print(f"  {e.entity}: score={e.score:.1f}, mentions={e.mentions}")
