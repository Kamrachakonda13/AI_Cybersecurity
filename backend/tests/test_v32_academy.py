from app.services.team_academy import academy_overview, recommended_curriculum
from app.services.sudo_arsenal import _all_tools


def test_every_registered_tool_has_markdown_help():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    docs=root/'docs'/'tools'
    tools=_all_tools()
    assert len(tools) >= 500
    missing=[]
    for t in tools:
        import re
        slug=re.sub(r'[^a-z0-9._-]+','-',t['id'].lower()).strip('-') or 'tool'
        if not (docs/f'{slug}.md').exists():
            missing.append(t['id'])
    assert not missing, missing[:20]


def test_academy_tracks():
    o=academy_overview()
    assert o['tool_count'] >= 500
    assert {'ai-security','soc-defender','red-team'} <= {x['id'] for x in o['tracks']}
    c=recommended_curriculum('ai-security')
    assert c['tool_count'] > 0
