## Concept

1. Mapping the file: The structure should logically map the `.viewer`.

## Quick Look

```graphviz
digraph G {
  compound=true;
  rankdir="LR"
  
  subgraph cluster_viewer {


    label = "Viewer"

        subgraph cluster_Controller {
            label = "Controller"
           node [shape=box] Mouse;
           node [shape=box] Key;
          node [shape=box] Selector;
          Mouse -> Selector

          }


        subgraph cluster_Action {
            label = "Action"
            node [shape=box] zoom_selected;
            node [shape=box] view_left;
            node [shape=box] view_shaded;
            node [shape=box] etc;


          }
        subgraph cluster_Scene {
            label = "Scene"
            node [shape=box] Camera;
            node [shape=box] Matrices;
            node [shape=box] Shader;
        }

        subgraph cluster_Objects {
            label = "Objects"
        node [shape=box] Collection;
        }

        node [shape=box] UI;
        node [shape=box] Plot;

        node [shape=box] Timer;
        node [shape=box] Worker;

         Key  -> etc [lhead=cluster_Action]
         etc  -> etc [ltail=cluster_Action]
    }


  subgraph cluster_Interactive {
    label = "Interactive"
    node [shape=box] user_key_mouse;
  }

  subgraph cluster_Scripted {
    label = "Scripted"
    node [shape=box] compas_scene;
  }

  subgraph cluster_Graphic {
    label = "Graphic"
    node [shape=box] screen_display;
  }



user_key_mouse -> Key [lhead=cluster_Controller]
compas_scene -> Collection [lhead=cluster_Objects]
screen_display -> Shader [lhead=cluster_Scene]



}

```

## Structure




    Plot -> UI
    Shader -> cluster_Scene
    cluster_Objects -> cluster_Scene
    c -> g [ltail=Selector,lhead=cluster_Scene];
    cluster_Action -> cluster_Scene
    Mouse -> cluster_Scene
