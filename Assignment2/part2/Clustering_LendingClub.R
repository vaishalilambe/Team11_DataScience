install.packages("dplyr")
library(dplyr)

install.packages("cluster")
library(cluster) # for gower similarity and pam


## Visualization 
install.packages("Rtsne")
library(Rtsne)

install.packages("ggplot2")
library(ggplot2)

LendingClubLoan <- read.csv("C:/Users/mahesh/Desktop/Data_Science/Assignment3/data/Cleaned_AcceptedLoanDataFinal.csv")

head(LendingClubLoan)

LendingClubLoan_Clustering <- dplyr::select(LendingClubLoan, -X)

set.seed(33) 
LendingClubLoan_Clustering <- LendingClubLoan_Clustering[sample(1:nrow(LendingClubLoan_Clustering),
                                                                5000, replace=FALSE), ]
str(LendingClubLoan_Clustering)

### Step 2 Calculating distance
gower_dist <- daisy(LendingClubLoan_Clustering, metric = "gower")

## Step 2-1 Checking attributes to ensure the correct methods are being used
# (I = interval, N = nominal)
summary(gower_dist)



##Outputing most similar pair
gower_mat <- as.matrix(gower_dist)

LendingClubLoan_Clustering[
  which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]),
        arr.ind = TRUE)[1, ], ]




## Step 2-3 Outputting most dissimilar pair
LendingClubLoan_Clustering[
  which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),
        arr.ind = TRUE)[1, ], ]


### Step 3 Selecting number of clusters 
sil_width <- c(NA)

for(i in 2:10){
  pam_fit <- pam(gower_dist,
                 diss = TRUE,
                 k = i)
  
  sil_width[i] <- pam_fit$silinfo$avg.width
}



# Plot sihouette width (higher is better, based on the result, 3  clusters yeil the highest value)
plot(1:10, sil_width,
     xlab = "Number of clusters",
     ylab = "Silhouette Width")
lines(1:10, sil_width)
plot.show()



### Step 4 Partitioning around medoids (PAM) 
## Step 4-1 Summary of clustering results
pam_fit <- pam(gower_dist, diss = TRUE, k = 3)

pam_results <- LendingClubLoan_Clustering %>%
  mutate(cluster = pam_fit$clustering) %>%
  group_by(cluster) %>%
  do(the_summary = summary(.))

pam_results$the_summary


## Step 4-2 Exemplars of each cluster
LendingClubLoan_Clustering[pam_fit$medoids, ]




## Step 4-3 Visualization with reduced-dimension 
tsne_obj <- Rtsne(gower_dist, is_distance = TRUE)

tsne_data <- tsne_obj$Y %>%
  data.frame() %>%
  setNames(c("X", "Y")) %>%
  mutate(cluster = factor(pam_fit$clustering))

ggplot(aes(x = X, y = Y), data = tsne_data) +
  geom_point(aes(color = cluster)) +
  ggtitle("Clusters on reduced-dimension")







## Step 4-4 Plotting clusters over two variables
Clustering <- LendingClubLoan_Clustering %>%
  mutate(Cluster = pam_fit$clustering)

ggplot(aes(x = loan_amnt, y = int_rate), data = Clustering) +
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")  

ggplot(aes(x =fico_range, y=dti), data = Clustering) + 
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")



### Step 5 Agglomerative hierarchical clustering
## Step 5-1 Computes agglomerative hierarchical clustering
agn <- agnes(gower_dist, metric = "manhattan", stand = FALSE)

plot(agn, main= "Hierarchical clustering")



HierarchicalCluster <- LendingClubLoan_Clustering %>%
  mutate(Cluster=cutree(agn1,2))

tsne_obj <- Rtsne(gower_dist, is_distance = TRUE)

tsne_data <- tsne_obj$Y %>%
  data.frame() %>%
  setNames(c("X", "Y")) %>%
  mutate(cluster = factor(cutree(agn1,2)))

ggplot(aes(x = X, y = Y), data = tsne_data) +
  geom_point(aes(color = cluster)) +
  ggtitle("Clusters on reduced-dimension Plot")



## Step 5-3 Visualization on two variables
ggplot(aes(x = loan_amnt, y = grade), data = HierarchicalCluster) +
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")

ggplot(aes(x = loan_amnt, y = int_rate), data = HierarchicalCluster) + 
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")






## Step 5-3 Visualization on two variables
ggplot(aes(x = loan_amnt, y = int_rate), data = HierarchicalCluster) +
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")

ggplot(aes(x = fico_range, y = dti), data = HierarchicalCluster) + 
  geom_point(aes(color = factor(Cluster))) +
  ggtitle("Clusters on two variables")
