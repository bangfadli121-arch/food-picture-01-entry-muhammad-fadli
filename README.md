![make.fun](https://img.shields.io/badge/make.fun-submission-6f42c1)
![food-picture-01](https://img.shields.io/badge/bounty-food--picture--01-f39c12)
![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)

A program that writes one mouth-watering food picture to /output/entry.png — a lavish ramen bowl with glossy chashu, jammy soft-boiled eggs, rising steam and chili-oil swirls — for make.fun's food-picture-01 bounty.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Referral: 8y9pksda

## Verify

```sh
sha256sum out/entry.png
cmp out/entry.png entry.png
```
