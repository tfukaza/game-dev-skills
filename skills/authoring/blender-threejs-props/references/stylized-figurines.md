# Stylized figurines

Use this guidance for simple miniature or low-poly people when the brief values a cohesive manufactured-figurine silhouette over anatomical detail.

## Build one readable body

Distinguish a connected silhouette from an object assembled from intersecting rounded primitives. When the user requests a cohesive body, model shared shoulder, armpit, neck and crotch topology; joining separate objects does not remove the assembled appearance. Keep the intended slight roundness in the torso and limbs without turning the character into a stack of ovals.

Plain shirts, trousers, shoes, skin and hair can be material regions on the same surface. Put topology along hems, cuffs, hairlines and shoe openings so low-resolution material borders remain clean. Verify actual mesh connectivity as well as front, side and three-quarter silhouettes. Preserve the requested height in scene units and compare it against the receiving tile, counters, platforms and seats.

## Rig and duplicate deliberately

Check deformed soles throughout a walk cycle. A foot IK target on the floor can still leave the shoe floating when the leg cannot reach; correct reach and pelvis motion, then compare the loop endpoints. Inspect sitting, raised-hand and other contact poses against the actual receiving prop instead of a generic floor-only rig test.

When copying a rigged figure, rebind armature modifiers, constraint targets and knee poles to that copy. Verify mesh-to-rig ownership, assigned actions and the active scene after reopening the saved file. Shared geometry is useful for crowds, but individual rigs, poses and palette assignments must still point to the intended instances. Deliver animation files with a useful scene active rather than only a library that opens on an empty scene.

Vary pose, skin, hair and clothing through controlled material or instance data. Keep the underlying proportions and clothing boundaries stable; random variation should not create a new body model or break rig bindings. Review crowd readability at the game camera as well as one isolated character.
