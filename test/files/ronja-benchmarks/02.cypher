match (toFrom:Entity{Id:{eId}}), toFrom-[toFrom_rel:read|wrote]->(segment:Segment), copy-[:of]->document-[documentSegment:containing]->segment, segment-[:in_thread]->(thread:Thread), (checkIgnoredWriter:Entity)-[:wrote]->segment where (checkIgnoredWriter.Rank > 0 or checkIgnoredWriter.Rank is null) return count(distinct thread) as ThreadCount, count(distinct segment) as SegmentCount skip 0