# Star 23 Jewellery Concierge

A branded Streamlit shopping assistant for Star 23 Handmade Jewellery. It helps visitors explore gift,
styling, sizing, and care questions without claiming access to live products, prices, or stock.

## Run locally

```bash
python -m pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
streamlit run streamlit_app.py
```

You can alternatively enter an API key in the app. For deployment, set `OPENAI_API_KEY` in Streamlit
secrets or the host environment. The optional `OPENAI_MODEL` environment variable defaults to
`gpt-4o-mini`.

## Tests

```bash
python -m unittest -v
```

## Recommended website improvements

The live site should be validated separately with browser and analytics access. Highest-impact ecommerce
enhancements are:

1. Put a clear value proposition and primary “Shop jewellery” action above the fold.
2. Add collection, material, price, colour, availability, and gift filters with useful empty states.
3. Give every product consistent photos, dimensions, materials, care, dispatch estimate, returns summary,
   accessibility-friendly alternative text, and an obvious add-to-basket control.
4. Show delivery costs and returns information before checkout; never surprise shoppers late in the funnel.
5. Make mobile navigation, tap targets, focus states, contrast, labels, and keyboard operation first-class.
6. Compress responsive images, lazy-load below-the-fold media, reduce third-party scripts, and monitor Core
   Web Vitals.
7. Add founder/making-process stories, verified reviews, secure-payment cues, and contact details near buying
   decisions to build trust.
8. Track search, filter use, product views, add-to-basket, checkout, purchase, errors, and abandonment. Use
   funnel evidence and usability tests rather than assumptions to prioritize changes.
9. Add unique page titles/descriptions, product structured data, canonical URLs, an XML sitemap, and helpful
   collection copy for search discovery.
10. Integrate this concierge with an approved, frequently refreshed catalogue feed before allowing it to
    recommend named products or quote commercial details.
