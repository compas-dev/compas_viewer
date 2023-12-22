#version 120

varying vec3 vcolor;
varying vec2 direction_2d;
uniform float aspect;


float DistToLine(vec2 pt1, vec2 pt2, vec2 testPt)
{
  vec2 lineDir = pt2 - pt1;
  vec2 perpDir = vec2(lineDir.y, -lineDir.x);
  vec2 dirToPt1 = pt1 - testPt;
  return abs(dot(normalize(perpDir), dirToPt1));
}

float DistToPt(vec2 pt, vec2 testPt)
{
  return length(pt - testPt);
}

bool isHead(vec2 xy, vec2 dir){
  float dis = dot(xy - vec2(0.5, 0.5), dir);
  vec2 end = vec2(0.5, 0.5) + dir * 0.5;
  float angle = acos(dot(-dir, normalize(xy - end))); 
  return angle < 0.3 && dis > 0.25;
}

bool isBody(vec2 xy, vec2 dir){
  float dis1 = dot(xy - vec2(0.5, 0.5), dir);
  float dis2 = DistToLine(vec2(0.5, 0.5), vec2(0.5, 0.5) + dir, xy);
  return dis2 <= 0.01 && (dis1 >= 0 && dis1 <= 0.25);
}

void main()
{   
    vec2 xy = gl_PointCoord;

    if (length(direction_2d) == 0){
      discard;
    }else{
      vec2 dir = vec2(direction_2d.x * aspect, -direction_2d.y);
      dir = normalize(dir);
      if (!isBody(xy, dir) && !isHead(xy, dir)) {
          discard;
      }

      gl_FragColor = vec4(vcolor, 1.0);

    }
}
