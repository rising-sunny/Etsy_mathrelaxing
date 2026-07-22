# Custom Pet Paint-by-Numbers

Made-to-order digital product: a customer sends a photo of their pet, and we
turn it into a multi-size paint-by-numbers download bundle.

## Where each piece lives

| Piece | Location |
|---|---|
| Conversion engine (`build_bundle`) + web admin page | `mathrelaxing.store` repo → `services/pet_paintbynumbers.py`, `routers/pet_admin.py` |
| Etsy listing images, listing creation, promo video | **this folder** |

The engine is intentionally in the website repo because it also powers the
in-browser admin tool (`/admin/pet`), where staff upload the buyer's photo and
get a private download link to paste into the Etsy reply.

## Operational flow (per order)

1. Buyer orders on Etsy and messages their pet photo.
2. Staff open `mathrelaxing.store/admin/pet`, upload the photo, get a private
   download link (`/pet/dl/<token>`).
3. Staff paste that link in the Etsy reply. Delivery stays on Etsy; only the
   conversion is automated (Etsy has no messaging API).

## Scripts here

- **`make_listing_images.py`** — builds the listing images (cover, sizes, photo
  guide, "photos to avoid", any-pet example). Expects source images alongside it
  (`lab_photo.webp`, `lab_bundle_dense/`, optional `lowcontrast_example.jpg`);
  writes to `./listing`.
- **`create_pet_listing.py`** — creates the Etsy **draft** listing (title,
  description, tags, price, made-to-order), uploads the images from `./listing`,
  and attaches the welcome PDF as the digital file. Runs from the repo root so
  `etsy_token.json` is found.
- **`make_paint_reveal.py <photo> [out.mp4]`** — promo video: the low-poly grid
  fills in one color at a time, square by square, ending on the finished
  portrait. 1080x1080 for social.

## Notes

- Draft listing: Etsy id `4541752186` (kept as DRAFT; activation is manual).
- Personalization must be enabled in the Etsy UI (the API field is deprecated).
- Dependencies: `scikit-learn` (KMeans, via the engine), `matplotlib`, `Pillow`,
  and `ffmpeg` for the promo video.
