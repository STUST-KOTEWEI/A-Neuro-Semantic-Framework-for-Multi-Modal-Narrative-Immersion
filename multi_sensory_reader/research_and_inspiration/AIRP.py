{\rtf1\ansi\ansicpg950\cocoartf2865
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from fastapi import FastAPI\
\
# \uc0\u24314 \u31435 \u19968 \u20491  FastAPI \u25033 \u29992 \u31243 \u24335 \u23526 \u20363 \
app = FastAPI()\
\
# \uc0\u23450 \u32681 \u19968 \u20491  API \u31471 \u40670  (endpoint)\
# \uc0\u30070 \u26377 \u20154 \u35370 \u21839 \u32178 \u31449 \u26681 \u30446 \u37636  ("/") \u26178 \u65292 \u22519 \u34892 \u36889 \u20491 \u20989 \u24335 \
@app.get("/")\
def read_root():\
    return \{"Hello": "World", "Project": "AI Multisensory Intelligent Reader"\}\
\
}