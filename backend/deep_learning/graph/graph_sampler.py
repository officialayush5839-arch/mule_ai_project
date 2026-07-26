from torch_geometric.loader import NeighborLoader
from torch_geometric.data import Data

class EnterpriseGraphSampler:
    """
    Scalable Mini-batch neighbor sampling for massive graphs.
    """
    @staticmethod
    def create_loader(
        data: Data, 
        batch_size: int = 1024,
        num_neighbors: list = [15, 10, 5],
        shuffle: bool = True
    ) -> NeighborLoader:
        """
        data: PyG Data object
        num_neighbors: list indicating how many neighbors to sample per hop. 
                       e.g. [15, 10, 5] means 3 hops.
        """
        return NeighborLoader(
            data,
            num_neighbors=num_neighbors,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=0 # Keep 0 for local windows tests
        )
