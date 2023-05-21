In the case of the PnP problem, we want to find the camera pose given associations between 3D points and their projections image plane.

A first way to express this problem mathematically is to cast it as a linear least squares problem. 
This approach is known as the DLT approach, and it is interesting because linear least-squares have a closed-form solution which can be found robustly using the Singular Value Decomposition.
However, this approach assumes that the camera pose P has 12 degrees of freedom when really it has only 6 (3 for the 3D rotation plus 3 for the 3D translation). 
To obtain a 6DOF camera pose from the result of this approach an approximation is needed (which is not covered by the linear cost function of the DLT), leading to an inaccurate solution.

A second way to express the PnP problem mathematically is to use the geometric error as a cost function,
and to find the camera pose that minimizes the geometric error. Since the geometric error is non-linear, 
this approach estimates the solution using iterative solvers, such as the Levenberg Marquardt algorithm. 
Such algorithms can take into account the 6 degrees of freedom of the camera pose, leading to accurate solutions. 
However, since they are iterative approaches, they need to be provided with an initial estimate of the solution, 
which in practice is often obtained using the DLT approach.