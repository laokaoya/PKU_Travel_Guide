# What is PKU Travel Guide?

## Background
- The project started in July 2023 when Peking University reopened for visits. At that time, I was in charge of student rights projects in the student union and noticed several issues with the official Peking University app: for example, some attractions were missing, the routes were too simple, and the introductions were dull and unengaging. Therefore, I decided to lead my department colleagues in creating a brand-new "Peking University Tourism Guide," aiming to showcase the most comprehensive attractions and provide the most personalized travel experience for visitors. 
- Since none of us specialized in design or computer science, the result might not have been perfect, but it was an interesting attempt, and we hoped it could truly help visitors touring Peking University.
- Over the course of a year, the project faced many challenges, with progress being stalled multiple times and team members undergoing several adjustments. After numerous content revisions and version iterations, we finally managed to realize the initial concept to a certain extent. However, the project is still far from being a fully developed and mature campus tour guide, with many areas needing improvement.
- The guide will be continuously updated, and we welcome your feedback. We also hope that more like-minded individuals will join us in improving the campus tour experience together!

## Project Introduction
- The project primarily uses Python, with PyQt5 for the user interface, and OpenStreetMap as the base map.
### Data Collection
- Coordinates: We explored the campus to discover and identify noteworthy spots for visitors, and marked them in Amap (AutoNavi) for record-keeping. Totally we collected 106 tourist attractions and another 30 locations for special activities design.
- hot_score and rate: We conducted visitor interviews, consulted senior students and professors, distributed surveys on campus forums, and gathered guides and reviews from external travel websites. Through this, we obtained the popularity and ratings of various campus attractions
- Features and description: We completed the summarization of key features as well as the generation of personalized descriptions for each spot.
![b928146d7f67b040f9680b81d203043](https://github.com/user-attachments/assets/93b8b2f0-87bd-4a27-b522-a8316bbf8a0d)
### Data Analysis
- Using a scoring system, we designed formulas and parameters to recommend different numbers and types of attractions based on the user's personalized input, and display tailored descriptions for each attraction.
- We acquire road network data from OpenStreetMap and use nearest neighbor and genetic algorithms to plan the most efficient routes.
- Design special campus tour activities, including "Yanyuan Ancient Tree Map," "Where Are the Animals in Yanyuan," "Hidden Corners," "Yanyuan’s Unique Stones and Sculptures," and "Campus Canteen Check-ins," and create corresponding maps for these activities.
### Test and feedback
- First Step: Completing internal team evaluations. The benchmark is tourism guides related to Peking University on Xiaohongshu, with a total of 28 articles collected (including visitor information and route options). If more than 70% of our recommended solutions are considered superior to the apps mentioned, we will pass the internal testing phase.
- Second Step: Releasing a test version on an anonymous campus forum for evaluation by Peking University students and faculty. Collecting opinions and feedback, and encourage them to recommend the app to friends and family visiting Peking University. The internal evaluation will last for two weeks, during which five surveys will be distributed, with a goal of collecting 300 responses.
→ Third Step: Launching the app on public platforms, making it available for general tourists to try out, and provide feedback channels for continuous improvement.


## Drawbacks and Update Goals
- Attempt to implement multiple language versions.
- Improve function implementations for more accurate recommendation algorithms.
- Integrate large model capabilities to provide more detailed attraction information and personalized descriptions.
- Finalize the app version and create a formal release version.
