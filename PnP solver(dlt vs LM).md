# In the case of the PnP problem, we want to find the camera pose given associations between 3D points and their projections image plane.




## DLT Method: 
The DLT method is a direct approach to solving the PnP problem. It involves setting up and solving a system of linear equations using the 3D-2D correspondences.
The DLT method is relatively straightforward and easy to implement. 
However, it does not explicitly consider the geometric constraints and may be sensitive to noise and outliers in the correspondences. 
this approach assumes that the camera pose P has 12 degrees of freedom when really it has only 6 (3 for the 3D rotation plus 3 for the 3D translation). 
To obtain a 6DOF camera pose from the result of this approach an approximation is needed (which is not covered by the linear cost function of the DLT), leading to an inaccurate solution.

 ## LM Optimization:
 The LM optimization method, on the other hand, is an iterative optimization approach that minimizes the reprojection error between the projected 3D points and the actual 2D points. 
 It leverages an optimization algorithm (such as the Levenberg-Marquardt algorithm) to iteratively refine the camera pose estimate. 
 The LM optimization method can handle noise and outliers more effectively and can incorporate additional constraints or priors on the camera pose if needed. 
 It also allows for the estimation of both the camera pose and intrinsic parameters simultaneously.
 
 
 # How to make Pnp differentiable？
 
 1. for DLT Method, we can use kornia library.
 2. for LM optimization, we can use EPro-PnP(2022 cvpr best student paper) or back_to_feature(2021 cvpr oral) 
