# assets/

## Supplied by the brand

| File | What |
| --- | --- |
| `logo.svg` | Two-colour artwork — brown script wordmark (#453529) + rose mincing-plate mark (#D06965). Use on paper, blush or cream. |
| `logo-light.svg` | Same artwork in paper (#FAF8F5) + coral (#EF5F63), for teal grounds and photography. |
| `logo-mark.svg` | The plate alone, rose. Favicons, tight headers, stamps. |
| `logo-mark-mono.svg` | The plate in `currentColor` — inline it as SVG to tint it; as an `<img>` it renders black. |
| `fonts/BourtonBase.ttf` | The display face. One weight, uppercase. Declared in `tokens/fonts.css`. |

The source upload was `uploads/kv.svg`. Its embedded `<style>` block was stripped (SVG style
elements do not survive this project's file handling), so the fills are written as
presentation attributes on each path — that is the only change made to the artwork.

## Still missing

| What | Source path on the live site |
| --- | --- |
| Venue photography (Majorstua) | `/static/img/majorstua/1..6.jpg`, `int_1..int_4.jpg` |
| Takeaway photography | `/static/img/takeaway/topp.jpg`, `1.jpg`, `2.jpg`, `3.jpg`, `6.jpg` |
| Press marks | `/static/img/takeaway/dagbladet.svg`, `finansavisen.svg`, `dice.svg` |
| Hero video | `/static/video/MJS-HH.mp4` |
| Text/label webfonts | none supplied — Newsreader + Barlow Condensed stand in |

Until the photography lands, every image is a labelled placeholder via
`components/content/PhotoFrame.jsx`. Icons come from Lucide over CDN (see ICONOGRAPHY in
`readme.md`).
