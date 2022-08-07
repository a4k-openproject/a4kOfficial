# a4kOfficial
Provider package for Seren which interfaces with dedicated add-ons for many popular streaming services. This package leverages [JustWatchAPI](https://github.com/dawoudt/JustWatchAPI) to discover streaming services (from [JustWatch](https://www.justwatch.com/)) which offer the requested content, and defers playback to the respective add-on(s).

# Supported Services
| Service         | Add-on                              | Plugin ID                         | Latest Tested Version |
|:----------------|:------------------------------------|:----------------------------------|----------------------:|
| BBC iPlayer     | [iPlayer WWW](#iplayer-www)         | `plugin.video.iplayerwww`         | `Untested`            |
| CuriosityStream | [CuriosityStream](#curiositystream) | `slyguy.curiositystream`          | `Untested`            |
| Disney+         | [Disney+](#disney)                  | `slyguy.disney.plus`              | `0.12.1`              |
| HBO Max         | [HBO Max](#hbo-max)                 | `slyguy.hbo.max`                  | `0.9.9`               |
| Hulu            | [Hulu](#hulu)                       | `slyguy.hulu`                     | `0.2.1`               |
| Netflix         | [Netflix](#netflix)                 | `plugin.video.netflix`            | `1.18.8+matrix.1`     |
| Paramount+      | [Paramount+](#paramount)            | `slyguy.paramount.plus`           | `0.5.2`               |
| Plex            | [Composite](#composite)             | `plugin.video.composite_for_plex` | `0.9.5+matrix.1`      |
| Prime Video     | [Prime Video](#prime-video)         | `plugin.video.amazon-test`        | `0.9.5+matrix.1`      |

Also included is a Kodi library scraper for local files, which needs no extra add-ons to be installed or any additional setup, and is enabled by default.

# Requirements
* Kodi Matrix 19.0 or greater
* Seren 2.2.2 or greater

# Installation
This package can be installed from "Web Location" in Seren, using the url: https://github.com/a4k-openproject/a4kOfficial/zipball/master.

Alternatively, open the URL above in any browser, save the resulting `.zip` file to some location, and "Browse" to it instead.

# Configuration
When installed for the first time, a prompt is shown asking which providers you would like to enable, with default selections based on which of the corresponding add-ons you also have installed. These selections can be toggled at this time, or at any subsequent time from Seren's Provider Manager.

# Recommended Settings for Seren
* Accounts
  - [x] `Enable Trakt Scrobbling`
* Scraping
  - [x] `Enable Preemptive Termination`
  - [x] `Terminate if Adaptive Sources are Found`
* Playback
  - [x] `Enable Smart Play`
  - [x] `Pre-emptive Scraping`
  - [x] `Enable Playing Next Dialog`

# Supported Add-ons
For most of the add-ons supported, there are a few settings which may require attention in order to maintain the best compatibility with these players. In general, the recommended settings for each add-on are meant to preserve the most functionality of both the playing add-on and Seren, ideally including the following where available:

* Consistent artwork and metadata
* Progress tracking with the service
* Progress tracking with Trakt
* Auto-play next episode
* Skip intro and/or credits
* Highest quality sources available
* Fewest clicks to playback

These features don't *always* work, notably with regards to artwork and metadata, as the playing add-on will usually use service-specific information where available. The general approach to the recommended settings below is to enable any "progress tracking" features (so that tracking works properly with the service), disable any "next episode" features (so that Seren's Playing Next feature will work properly), and optionally enable any "skip intro and/or credits" features (at user's discretion). Any settings which are not mentioned are recommended to be left at their default value.

All of these add-ons require some kind of login process, which is usually initiated automatically whenever the add-on is opened for the first time, and will be the main requirement for any of them to playback sources (or, indeed, work at all).

## iPlayer WWW
### Installation
Offical Repository Install:
* Navigate to `Settings -> Add-ons -> Install from repository`
* Choose `Kodi Repository`
* Choose `Video Add-ons`
* Choose `iPlayer WWW`
* Choose `Install`

### Recommended Settings
All defaults should be fine, though this one hasn't been tested yet.

## CuriosityStream
### Installation
Enable Unknown Sources:
* Navigate to `Settings -> System -> Add-ons`
* Change the settings level to either `Advanced` or `Expert`
* Enable `Unknown sources`
* (Highly Recommended) Change `Update official add-ons from` to `Any repositories`
* (Highly Recommended) Change `Updates` to `Notify, but don't install updates`
* (Recommended) Enable `Show notifications`

Add New Source:
* Navigate to `Settings -> File Manager`
* Choose `Add source`
* Add the source: https://k.slyguy.xyz/
* Name the source: `repository.slyguy`

Install Repository:
* Navigate to `Settings -> Add-ons -> Install from zip...`, and accept the prompt
* Choose `repository.slyguy`
* Choose `repository.slyguy.zip`, and accept the prompt

SlyGuy Repository Install:
* Navigate to `Settings -> Add-ons -> Install from repository`
* Choose `SlyGuy Repository`
* Choose `Video Add-ons`
* Choose `CuriosityStream`
* Choose `Install`

### Recommended Settings
* Playback
  - `Playback Quality`: `Best`

## Disney+
### Installation
* [Official Install Guide](https://www.matthuisman.nz/2020/04/disney-plus-kodi-add-on.html)

### Recommended Settings
* Look & Feel
  - [ ] `Play Next Episode`
  - [ ] `Play Next Recommended Movie`
  - [x] `Skip Intros` (Optional)
  - [x] `Skip Credits` (Optional)
  - [x] `Disney+ Sync Playback`
* Playback
  - `Playback Quality`: `Best`


## HBO Max
### Installation
* [Official Install Guide](https://www.matthuisman.nz/2020/11/hbo-max-kodi-add-on.html)

### Recommended Settings
* Look & Feel
  - [x] `Skip Intros` (Optional)
  - [x] `Skip Credits` (Optional)
  - [ ] `Play Next Episode`
  - [ ] `Play Next Recommended Movie`
  - [x] `HBO Max Sync Playback`
* Playback
  - `Playback Quality`: `Best`
  - [x] `Dolby Digital (AC-3)`
  - [x] `Dolby Digital Plus (EC-3)`
  - [x] `Dolby Atmos`
  - [x] `H.265`
  - [x] `4K`
  - [x] `Dolby Vision`

## Hulu
### Installation
* [Official Install Guide](https://www.matthuisman.nz/2021/10/hulu-kodi-add-on.html)

### Recommended Settings
* General
  - [x] `Hulu Sync Playback`
* Playback
  - `Playback Quality`: `Best`
  - [x] `EC3`
  - [x] `H265`
  - [x] `4K`

## Netflix
### Installation
* [Official Install Guide](https://github.com/CastagnaIT/plugin.video.netflix)

Besides the settings listed below, ensure that you've logged into the add-on using your Netflix credentials, and chosen a default profile. If a default profile isn't chosen ahead of time, a "Choose Profile" prompt will be shown before playback starts.

### Choosing Default Profile
After successfully authenticating, the Profiles menu is shown. Highlight the profile you'd like to use for playback, open the context menu (`C`, right-click, or long-press), and choose `Set for auto-selection`. Repeat these steps once more, but choose `Set for library playback`. This ensures that the chosen profile will be used by default whenever one of our sources (or anything played by the Netflix add-on) is played. This menu can be reached again, if needed, by simply choosing `Profiles` from the root menu of the add-on.

### Recommended Settings
* General
  - [x] `Synchronize the watched status of the videos with Netflix`
* Playback
  - [x] `Remember audio / subtitle preferences`
  - [x] `Prefer stereo tracks by default`
  - [x] `Ask to skip intro and recap` (Optional)

## Paramount+
* [Official Install Guide](https://www.matthuisman.nz/2021/06/paramount-plus-kodi-add-on.html)

### Installation
### Recommended Settings
* Playback
  - `Playback Quality`: `Best`
  - [x] `Dolby Digital (AC-3)`
  - [x] `Dolby Digital Plus (EC-3)`
  - [x] `Dolby Atmos`
  - [x] `H.265`
  - [x] `4K`
  - [x] `Dolby Vision`

## Composite
### Installation
Offical Repository Install:
* Navigate to `Settings -> Add-ons -> Install from repository`
* Choose `Kodi Repository`
* Choose `Video Add-ons`
* Choose `Composite`
* Choose `Install`

### Recommended Settings
* Playback
  - `Stream from PMS`: `Auto`
  - [x] `Intro skipping` (Optional)
  - [ ] `Always Transcode`
  - [ ] `Transcode > 8-bit`
  - [ ] `Transcode > 1080p`
  - [ ] `Transcode HEVC`
* Advanced
  - [x] `Use full resolution thumbs`
  - [x] `Use full resolution fanart`

## Prime Video
### Installation
* [Official Install Guide](https://github.com/Sandmann79/xbmc)

### Recommended Settings
* General
  - `Playback with`: `Input Stream`
  - `Prefered Host`: `Auto`
  - `Intro/Recap scenes processing`: `Show Skip Button` (Optional)
